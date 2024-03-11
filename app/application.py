from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from starlette.responses import Response

from app import config
from app.config import log_config
from app.routers import demo


@asynccontextmanager
async def lifespan(_: FastAPI):
    config.configure_app()

    # We must configure app logging after uvicorn started,
    # thus the file handler should exist for reusing.
    log_config.configure_app_logging()

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
        request, HTTPException(500, "Internal server error", headers={"X-Request-ID": correlation_id.get() or ""})
    )
