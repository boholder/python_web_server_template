import logging
import logging.config
import logging.handlers
import os
from pathlib import Path

from asgi_correlation_id import CorrelationIdFilter

LOG_LEVEL = "INFO"

# time | log level | logger name | trace id | process id | thread id | message
# %(levelname)8s: max 8 characters for "CRITICAL"
# ref: https://docs.python.org/3/library/logging.html#logrecord-attributes
LOG_FORMAT_PATTERN = "%(asctime)s|%(levelname)-8s|%(name)s|%(correlation_id)s|%(process)d|%(thread)d| %(message)s"

TRACE_ID_FILTER = CorrelationIdFilter(name="trace_id_filter", uuid_length=16, default_value="-")

_HOME_PATH = os.path.expanduser("~")
_LOG_FILE_PATH = Path(_HOME_PATH + "/logs/app.log")
# create parent directories of log file if these do not exist
_LOG_FILE_PATH.parent.mkdir(exist_ok=True, parents=True)

# It will be added to logging config as "file_handler" for uvicorn config initializing
FILE_HANDLER_CONFIG = {
    "formatter": "default",
    # ref: https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
    "class": "logging.handlers.TimedRotatingFileHandler",
    "filename": _LOG_FILE_PATH,
    "when": "midnight",
    "backupCount": 7,
    "encoding": "utf-8",
}


def configure_app_logging(file_handler: logging.Handler) -> None:
    """
    :param file_handler: Reuse the file handler instance created by uvicorn
    """

    console_handler = logging.StreamHandler()
    console_handler.addFilter(TRACE_ID_FILTER)
    logging.basicConfig(
        handlers=[console_handler, file_handler],
        level=LOG_LEVEL,
        format=LOG_FORMAT_PATTERN)
