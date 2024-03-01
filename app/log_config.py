import logging.config
import os
from pathlib import Path

from asgi_correlation_id import CorrelationIdFilter

HOME_PATH = os.path.expanduser("~")
LOG_FILE_PATH = Path(HOME_PATH + "/logs/app.log")
LOG_FILE_PATH.parent.mkdir(exist_ok=True, parents=True)

TRACE_ID_FILTER = CorrelationIdFilter(name="trace_id_filter", uuid_length=16, default_value="-")

LOG_FORMAT_PATTERN = "%(asctime)s|%(levelname)-8s|%(name)s|%(correlation_id)s|%(process)d|%(thread)d| %(message)s"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            "uuid_length": 16,
            "default_value": "-",
        },
    },
    "formatters": {
        "default": {
            # time | log level | logger name | trace id | process id | thread id | message
            # %(levelname)8s: max 8 characters for "CRITICAL"
            # ref: https://docs.python.org/3/library/logging.html#logrecord-attributes
            "format": LOG_FORMAT_PATTERN,
        },
        "access": {
            # time | log level | logger name | trace id | process id | thread id | message
            # %(levelname)8s: max 8 characters for "CRITICAL"
            # ref: https://docs.python.org/3/library/logging.html#logrecord-attributes
            "format": LOG_FORMAT_PATTERN,
        }
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "default",
            # ref: https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "filters": ["correlation_id"],
            "propagate": "no",
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "filters": ["correlation_id"],
            "propagate": "no",
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
        "filters": ["correlation_id"],
        "propagate": "no",
    }
}


def config_app_logging() -> None:
    console_handler = logging.StreamHandler()
    console_handler.addFilter(TRACE_ID_FILTER)
    logging.basicConfig(
        handlers=[console_handler],
        level="INFO",
        format=LOG_FORMAT_PATTERN)
