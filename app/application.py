import logging
import logging.config
import logging.handlers
from contextlib import asynccontextmanager

from asgi_correlation_id import correlation_id, CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from starlette.responses import Response

from app import log_config
from app.routers import demo


def find_log_file_handler() -> logging.Handler:
    """
    I don't want to create two file logging handlers for one same file,
    although it works, I'm not sure if this solution is reliable under heavy workload.
    """

    # ref: https://stackoverflow.com/a/55400327/11397457
    l = logging.Logger.manager.loggerDict["uvicorn"]
    for h in l.handlers:
        if isinstance(h, logging.handlers.TimedRotatingFileHandler):
            return h
    raise Exception("Can not found file handler.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # We must configure app logging after uvicorn started, thus the file handler should exists for reusing.
    log_config.configure_app_logging(find_log_file_handler())
    global log
    log = logging.getLogger(__name__)
    yield


APP = FastAPI(lifespan=lifespan)
APP.include_router(demo.router)
APP.add_middleware(CorrelationIdMiddleware)


@APP.exception_handler(Exception)
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
