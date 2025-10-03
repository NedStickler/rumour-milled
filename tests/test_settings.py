import os
from rumour_milled.settings import load_settings
from dotenv import load_dotenv


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    settings = load_settings()
    assert settings.env == "local"
    assert settings.log_level == "INFO"
    assert settings.aws_region == "eu-west-2"


def test_settings_existing_envs_match(monkeypatch):
    load_dotenv()
    settings = load_settings()
    assert settings.env == os.getenv("ENV")
    assert settings.log_level == os.getenv("LOG_LEVEL")
    assert settings.aws_region == os.getenv("AWS_REGION")


def test_settings_env_overrides(monkeypatch):
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")
    settings = load_settings()
    assert settings.env == "test"
    assert settings.log_level == "DEBUG"
    assert settings.aws_region == "eu-central-1"
