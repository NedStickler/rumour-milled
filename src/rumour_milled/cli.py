import typer
import uuid
import pytest
import subprocess
from rumour_milled import log
from rumour_milled.settings import load_settings, Settings
from dotenv import load_dotenv
from typing import Literal


app = typer.Typer(no_args_is_help=True, add_completion=False)


def _boot() -> Settings:
    load_dotenv()
    settings = load_settings()
    log.setup_logging(settings.log_level)
    run_id = uuid.uuid4().hex[:12]
    log.bind_run(run_id)
    log.bind_component("cli")
    log.log("boot", env=settings.env, log_level=settings.log_level, run_id=run_id)
    return settings


def _run(cmd: list[str]):
    subprocess.run(cmd, check=True)


@app.command()
def hello(name: str) -> None:
    _boot()
    log.log(f"Hello, {name}!")


@app.command()
def ping() -> None:
    _boot()
    log.log("ping", status="ok")


# TODO: Add module type hint as `module: Literal["all", "scraping", ...] = "all` when Typer adds support (PR was completed 19/09/2025)
@app.command()
def test(module = "all", pytest_args: list[str] = []) -> None:
    _boot()
    log.log("run_tests", module=module, pytest_args=pytest_args)

    if module == "all":
        path = "."
    elif module == "scraping":
        path = "tests/scraping"
    elif module == "storage":
        path = "tests/storage"

    pytest.main([path] + pytest_args)


@app.command()
def up(makefile_path: str = "infra/", env: str = "local") -> None:
    _boot()
    _run(["make", "-C", f"{makefile_path}", f"ENV={env}", "all"])
    log.log("up", env=env)


@app.command()
def down(makefile_path: str = "infra/") -> None:
    _boot()
    _run(["make", "-C", f"{makefile_path}", "down"])
    log.log(down)


if __name__ == "__main__":
    app()
