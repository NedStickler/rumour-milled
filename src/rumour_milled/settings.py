import os
from dataclasses import dataclass


def env_str(name: str, default: str) -> str:
    var = os.getenv(name)
    return var if var not in (None, "") else default


@dataclass(frozen=True)
class Settings:
    env: str
    log_level: str
    aws_region: str
    makefile_path: str


def load_settings() -> Settings:
    return Settings(
        env=env_str("ENV", "local"),
        log_level=env_str("LOG_LEVEL", "INFO").upper(),
        aws_region=env_str("AWS_REGION", "eu-west-2"),
        makefile_path=env_str("MAKEFILE_PATH", "infra/")
    )