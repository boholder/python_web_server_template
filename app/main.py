import logging
import logging.config
import logging.handlers
from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import correlation_id, CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from starlette.responses import Response
from uvicorn.config import LOGGING_CONFIG

import log_config
from routers import demo

log: logging.Logger

FILE_HANDLER_NAME = "file_handler"


def find_log_file_handler() -> logging.Handler:
    # ref: https://stackoverflow.com/a/55400327/11397457
    l = logging.Logger.manager.loggerDict["uvicorn"]
    for h in l.handlers:
        if isinstance(h, logging.handlers.TimedRotatingFileHandler):
            return h
    raise Exception("Can not found file handler.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # We must configure app logging after uvicorn started, thus the file handler should exists for reusing.
    log_config.configure_app_logging(find_log_file_handler())
    global log
    log = logging.getLogger(__name__)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(demo.router)
app.add_middleware(CorrelationIdMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    """
    ref: https://github.com/snok/asgi-correlation-id?tab=readme-ov-file#fastapi-1
    """
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            'Internal server error',
            headers={'X-Request-ID': correlation_id.get() or ""}
        ))


def configure_uvicorn_logging():
    """Must configure the uvicorn.config.LOGGING_CONFIG within the same module that runs uvicorn.run()."""
    extra_filters = [log_config.TRACE_ID_FILTER]
    for handler in LOGGING_CONFIG["handlers"].values():
        handler["filters"] = handler["filters"] + extra_filters if "filters" in handler else extra_filters
    for formatter in LOGGING_CONFIG["formatters"].values():
        formatter["fmt"] = log_config.LOG_FORMAT_PATTERN

    LOGGING_CONFIG["handlers"][FILE_HANDLER_NAME] = log_config.FILE_HANDLER_CONFIG
    # There are three loggers in uvicorn default logging config: "uvicorn", "uvicorn.access", "uvicorn.error".
    # We need to add "file_handler" to logger "uvicorn" and "uvicorn.access"
    # since logger "uvicorn.error" will propagate the log to the other two.
    for logger in LOGGING_CONFIG["loggers"].values():
        if "handlers" in logger:
            logger["handlers"] += [FILE_HANDLER_NAME]


if __name__ == "__main__":
    configure_uvicorn_logging()
    uvicorn.run("main:app", port=8000, reload=True)
