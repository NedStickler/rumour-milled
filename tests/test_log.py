import json
import logging
from rumour_milled.log import setup_logging, bind_run, bind_component, log, warn, error


def test_log(capsys):
    setup_logging("INFO")
    log("hello")
    out = json.loads(capsys.readouterr().out)
    assert out["level"] == "info"


def test_warn(capsys):
    setup_logging("INFO")
    warn("hello")
    out = json.loads(capsys.readouterr().out)
    assert out["level"] == "warning"


def test_error(capsys):
    setup_logging("INFO")
    error("hello")
    out = json.loads(capsys.readouterr().out)
    assert out["level"] == "error"


def test_json_shape(capsys):
    setup_logging("INFO")
    bind_run("123")
    bind_component("unit-test")
    log("hello", test="yes")
    out = json.loads(capsys.readouterr().out)
    assert "ts" in out
    assert out["level"] == "info"
    assert out["logger"] == "rm"
    assert out["event"] == "hello"
    assert out["run_id"] == "123"
    assert out["component"] == "unit-test"
    assert out["test"] == "yes"


def test_captured_exception(capsys):
    setup_logging("INFO")

    test_dict = {}
    try:
        test_dict["test"]
    except KeyError:
        logging.getLogger("rm").exception("explosion")
    
    out = json.loads(capsys.readouterr().out)
    assert out["event"] == "explosion"
    assert out["level"] == "error"
    assert out["exc_type"] == "KeyError"