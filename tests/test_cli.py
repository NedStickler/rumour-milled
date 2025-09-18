from typer.testing import CliRunner
from rumour_milled.cli import app
import json


runner = CliRunner()


def _last_json_line(text: str) -> dict:
    lines = [line for line in text.splitlines() if line.split()]
    return json.loads(lines[-1])


def test_hello():
    result = runner.invoke(app, ["hello", "test"])
    assert result.exit_code == 0
    out = _last_json_line(result.stdout)
    assert out["event"] == "Hello, test!"


def test_ping():
    result = runner.invoke(app, ["ping"])
    assert result.exit_code == 0
    out = _last_json_line(result.stdout)
    assert out["event"] == "ping"
    assert out["status"] == "ok"