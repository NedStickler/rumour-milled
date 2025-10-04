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


@app.command()
def test(path: str = "tests/") -> None:
    settings = _boot()
    log.log("test", pytest_path=path)
    _run(["make", "-C", f"{settings.makefile_path}", f"ENV={settings.env}", f"pytest_path={path}"])


@app.command()
def up() -> None:
    settings = _boot()
    _run(["make", "-C", f"{settings.makefile_path}", f"ENV={settings.env}", "all"])
    log.log("up", env=settings.env)


@app.command()
def down() -> None:
    settings = _boot()
    _run(["make", "-C", f"{settings.makefile_path}", "down"])
    log.log("down")


@app.command()
def build() -> None:
    settings = _boot()
    _run(["make", "-C", f"{settings.makefile_path}", "build"])
    log.log("build")


@app.command()
def all() -> None:
    settings = _boot()
    _run(["make", "-C", f"{settings.makefile_path}", "all"])
    log.log("all")


if __name__ == "__main__":
    app()
