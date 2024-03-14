import uvicorn
from uvicorn.config import LOGGING_CONFIG

from app import config
from app.config import log_config


def _configure_uvicorn_logging():
    """Must configure the uvicorn.config.LOGGING_CONFIG within the same module that runs uvicorn.run()."""
    extra_filters = [log_config.TRACE_ID_FILTER]
    for handler in LOGGING_CONFIG["handlers"].values():
        handler["filters"] = handler["filters"] + extra_filters if "filters" in handler else extra_filters
    for formatter in LOGGING_CONFIG["formatters"].values():
        formatter["fmt"] = config.CONFIG.app.log_format

    file_handler_name = "file_handler"
    LOGGING_CONFIG["handlers"][file_handler_name] = log_config.get_file_handler_config()

    # There are three loggers in uvicorn default logging config: "uvicorn", "uvicorn.access", "uvicorn.error".
    # We need to add "file_handler" to logger "uvicorn" and "uvicorn.access"
    # since logger "uvicorn.error" will propagate the log to the other two.
    for logger in LOGGING_CONFIG["loggers"].values():
        if "handlers" in logger:
            logger["handlers"] += [file_handler_name]


def main():
    config.configure_app()
    _configure_uvicorn_logging()
    uvicorn.run(
        "app.application:APP",
        host=config.CONFIG.app.host,
        port=config.CONFIG.app.port,
        reload=config.CONFIG.app.debug_mode,
    )


if __name__ == "__main__":
    main()
