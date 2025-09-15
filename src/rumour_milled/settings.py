import os
from dataclasses import dataclass


def _get(name: str, default: str) -> str:
    var = os.getenv(name)
    return var if var not in (None, "") else default


@dataclass(frozen=True)
class Settings:
    env: str = _get("ENV", "dev")
    log_level: str = _get("LOG_LEVEL", "INFO").upper()
    aws_region: str = _get("AWS_REGION", "eu-west-2")
    s3_bucket: str = _get("S3_BUCKET", "rm-dev-s3-bucket")


def load_settings() -> Settings:
    return Settings()