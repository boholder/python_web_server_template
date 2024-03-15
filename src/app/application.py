import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from starlette.responses import Response

from app import config
from app.routers import demo

log: logging.Logger


async def _on_app_start():
    config.configure_app()
    # We must configure app logging after uvicorn started,
    # thus the file handler should exist for reusing.
    config.configure_app_logging()
    global log
    log = logging.getLogger(__name__)
    log.debug(f"Starting application with following configuration: {config.CONFIG}")

    # nacos.register_onto_nacos()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _on_app_start()
    yield


FASTAPI_APP = FastAPI(lifespan=lifespan)
FASTAPI_APP.include_router(demo.router)
# noinspection PyTypeChecker
# Since CorrelationIdMiddleware isn't a fastapi specific middleware,
# its type is not fit fastapi type.
FASTAPI_APP.add_middleware(CorrelationIdMiddleware)


@FASTAPI_APP.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    """
    ref: https://github.com/snok/asgi-correlation-id?tab=readme-ov-file#fastapi-1
    """

    log.error("Caught an unhandled exception", exc_info=exc)
    return await http_exception_handler(
        request, HTTPException(500, "Internal server error", headers={"X-Request-ID": correlation_id.get() or ""})
    )
