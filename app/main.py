import logging
import logging.config
import logging.handlers
from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import correlation_id, CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel
from starlette.responses import Response
from uvicorn.config import LOGGING_CONFIG

import log_config

log: logging.Logger


class Item(BaseModel):
    name: str
    price: float


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
app.add_middleware(CorrelationIdMiddleware)


@app.get("/")
def read_root():
    log.info("info log")
    log.debug("debug log")
    log.error("error log")
    return {"Hello": "World"}


@app.get("/get/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/post")
def post_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}


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
    extra_filters = [log_config.TRACE_ID_FILTER]
    for handler in LOGGING_CONFIG["handlers"].values():
        handler["filters"] = handler["filters"] + extra_filters if "filters" in handler else extra_filters
    for formatter in LOGGING_CONFIG["formatters"].values():
        formatter["fmt"] = log_config.LOG_FORMAT_PATTERN

    LOGGING_CONFIG["handlers"][FILE_HANDLER_NAME] = log_config.FILE_HANDLER_CONFIG
    for logger in LOGGING_CONFIG["loggers"].values():
        if "handlers" in logger:
            logger["handlers"] += [FILE_HANDLER_NAME]


if __name__ == "__main__":
    configure_uvicorn_logging()
    uvicorn.run("main:app", port=8000, reload=True)
