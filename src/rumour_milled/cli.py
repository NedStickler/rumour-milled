import typer
import uuid
from rumour_milled import log
from rumour_milled.settings import load_settings
from dotenv import load_dotenv


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


if __name__ == "__main__":
    app()