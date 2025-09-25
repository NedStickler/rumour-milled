import typer
import uuid
import pytest
from rumour_milled import log
from rumour_milled.settings import load_settings
from dotenv import load_dotenv
from typing import Literal


app = typer.Typer(no_args_is_help=True, add_completion=False)


def _boot():
    load_dotenv()
    settings = load_settings()
    log.setup_logging(settings.log_level)
    run_id = uuid.uuid4().hex[:12]
    log.bind_run(run_id)
    log.bind_component("cli")
    log.log("boot", env=settings.env, log_level=settings.log_level, run_id=run_id)
    return settings


@app.command()
def hello(name: str) -> None:
    _boot()
    log.log(f"Hello, {name}!")


@app.command()
def ping():
    _boot()
    log.log("ping", status="ok")


# TODO: Add module type hint as `module: Literal["all", "scraping", ...] = "all` when Typer adds support (PR was completed 19/09/2025)
@app.command()
def run_tests(module="all", pytest_args: list[str] = []):
    _boot()
    log.log("run_tests", module=module, pytest_args=pytest_args)

    if module == "all":
        path = "."
    elif module == "scraping":
        path = "tests/scraping"
    elif module == "storage":
        path = "tests/storage"

    pytest.main([path] + pytest_args)


if __name__ == "__main__":
    app()
