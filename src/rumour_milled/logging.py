import contextvars
import logging
import json
import sys
from datetime import datetime, timezone


RUN_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("RUN_ID", default=None)
COMPONENT: contextvars.ContextVar[str | None] = contextvars.ContextVar("COMPONENT", default=None)


class JsonFormatter(logging.formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).isoformat()
        base = {
            "ts": ts,
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": record.getMessage()
        }

        run_id = RUN_ID.get()
        component = COMPONENT.get()
        if run_id:
            base["run_id"] = run_id
        if component:
            base["component"] = component

        kv = getattr(record, "kv", None)
        if isinstance(kv, dict):
            base.update(kv)
        if record.exc_info:
            base["exc_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None

        return json.dumps(base, ensure_ascii=False)
    
def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

def bind_run(run_id: str) -> None:
    RUN_ID.set(run_id)


def bind_component(component: str) -> None:
    COMPONENT.set(component)


def log(event: str, **kv) -> None:
    logging.getLogger("rm").info(event, extra={"kv": kv} if kv else None)

    
def warn(event: str, **kv) -> None:
    logging.getLogger("rm").warning(event, extra={"kv": kv} if kv else None)

    
def error(event: str, **kv) -> None:
    logging.getLogger("rm").error(event, extra={"kv": kv} if kv else None)