import logging
import logging.config
import logging.handlers
from contextlib import asynccontextmanager

from asgi_correlation_id import correlation_id, CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from starlette.responses import Response

import log_config
from routers import demo, heavy_task


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
app.include_router(heavy_task.router)
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
