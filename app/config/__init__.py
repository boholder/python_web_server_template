import argparse
import os
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator


def get_default_log_file_path() -> Path:
    """~/logs/app.log"""

    home = os.path.expanduser("~")
    return Path(home + "/logs/app.log").absolute()


# noinspection PyNestedDecorators
# to suppress false positive on overlapping decorators
# ref: https://youtrack.jetbrains.com/issue/PY-34368
class AppConfigs(BaseModel):
    """Contains the configuration for this application."""

    log_level: str = "INFO"
    log_file_path: Path = get_default_log_file_path()

    @field_validator("log_file_path")
    @classmethod
    def post_log_file_path(cls, v: Path) -> Path:
        # Resolve path to absolute
        v = v.absolute()
        # Create parent directory if it's not default log path and it doesn't exist
        if v != get_default_log_file_path():
            v.parent.mkdir(exist_ok=True, parents=True)
        return v

    debug_mode: bool = False


# Global configuration object
# initialize with default values
CONFIG: AppConfigs = AppConfigs()

ARG_PARSER = argparse.ArgumentParser(description="Web Server")
ARG_PARSER.add_argument("-c", "--config", help="Path of the config file", type=Path)
ARG_PARSER.add_argument("--debug", help="Enable debug mode", action="store_true")


def get_command_args(args: list[str] | None = None) -> argparse.Namespace:
    args = sys.argv[1:] if args is None else args
    return ARG_PARSER.parse_args(args)


def configure_app():
    args = get_command_args()

    if config_file_path := load_config_file_if_passed(args):
        configure_app_with(config_file_path)

    configure_debug_mode(args)


def load_config_file_if_passed(args: argparse.Namespace) -> Path | None:
    if cfg_path := args.config:
        abs_path = Path.resolve(Path(cfg_path))
        return abs_path


def configure_app_with(config_file_path: Path):
    file_content: dict
    with open(config_file_path, encoding="utf-8") as f:
        file_content = yaml.safe_load(f)

    parsed = AppConfigs.model_validate(file_content["app"])
    global CONFIG
    CONFIG = parsed


def configure_debug_mode(args: argparse.Namespace):
    if args.debug:
        global CONFIG
        CONFIG.debug_mode = True
        CONFIG.log_level = "DEBUG"
