import uvicorn

from app import config
from app.config import log_config


def main():
    config.configure_app()
    log_config.configure_uvicorn_logging()
    uvicorn.run(
        "app.application:FASTAPI_APP",
        host=config.CONFIG.app.host,
        port=config.CONFIG.app.port,
        reload=config.CONFIG.app.debug_mode,
    )


if __name__ == "__main__":
    main()
