import logging

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel
from starlette.responses import Response
from uvicorn.config import LOGGING_CONFIG

import log_config

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)

log_config.config_app_logging()
log = logging.getLogger(__name__)


class Item(BaseModel):
    name: str
    price: float


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


def config_uvicorn_logging():
    LOGGING_CONFIG["handlers"]["access"]["filters"] = [log_config.TRACE_ID_FILTER]
    LOGGING_CONFIG["handlers"]["default"]["filters"] = [log_config.TRACE_ID_FILTER]
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = log_config.LOG_FORMAT_PATTERN
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = log_config.LOG_FORMAT_PATTERN


if __name__ == "__main__":
    config_uvicorn_logging()
    uvicorn.run("main:app", port=8000, reload=True)
