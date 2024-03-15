import logging
import logging.config
import logging.handlers

import uvicorn
from asgi_correlation_id import CorrelationIdFilter

from app import config

_TRACE_ID_FILTER = CorrelationIdFilter(name="trace_id_filter", uuid_length=16, default_value="-")


def configure_uvicorn_logging():
    extra_filters = [_TRACE_ID_FILTER]
    for handler in uvicorn.config.LOGGING_CONFIG["handlers"].values():
        handler["filters"] = handler["filters"] + extra_filters if "filters" in handler else extra_filters
    for formatter in uvicorn.config.LOGGING_CONFIG["formatters"].values():
        formatter["fmt"] = config.CONFIG.app.log_format

    file_handler_name = "file_handler"
    uvicorn.config.LOGGING_CONFIG["handlers"][file_handler_name] = _get_file_handler_config()

    # There are three loggers in uvicorn default logging config: "uvicorn", "uvicorn.access", "uvicorn.error".
    # We need to add "file_handler" to logger "uvicorn" and "uvicorn.access"
    # since logger "uvicorn.error" will propagate the log to the other two.
    for logger in uvicorn.config.LOGGING_CONFIG["loggers"].values():
        if "handlers" in logger:
            logger["handlers"] += [file_handler_name]


def _get_file_handler_config() -> dict:
    """It will be added to logging config as "file_handler" for uvicorn config initializing."""
    return {
        "formatter": "default",
        # ref: https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
        "class": "logging.handlers.TimedRotatingFileHandler",
        "filename": config.CONFIG.app.log_file_path,
        "when": "midnight",
        "backupCount": 7,
        "encoding": "utf-8",
    }


def configure_app_logging(file_handler: logging.Handler | None = None) -> None:
    if file_handler is None:
        file_handler = _find_log_file_handler()

    console_handler = logging.StreamHandler()
    console_handler.addFilter(_TRACE_ID_FILTER)
    logging.basicConfig(
        handlers=[console_handler, file_handler], level=config.CONFIG.app.log_level, format=config.CONFIG.app.log_format
    )


def _find_log_file_handler() -> logging.Handler:
    """
    Reuse the file handler instance created by uvicorn.
    I don't want to create two file logging handlers for one same file,
    although it works, I'm not sure if this solution is reliable under heavy workload.
    """

    # ref: https://stackoverflow.com/a/55400327/11397457
    uvicorn_logger = logging.Logger.manager.loggerDict["uvicorn"]
    for h in uvicorn_logger.handlers:
        if isinstance(h, logging.handlers.TimedRotatingFileHandler):
            return h
    raise Exception("Can not found file handler.")
