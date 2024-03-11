import argparse
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel


class AppConfigs(BaseModel):
    """Contains the configuration for this application."""

    log_level: str = "INFO"
    debug_mode: bool = False


# Global configuration object
# initialize with default values
CONFIG: AppConfigs = AppConfigs()

ARG_PARSER = argparse.ArgumentParser(description="Web Server")
ARG_PARSER.add_argument("-c", "--config", help="Path of the config file", type=Path)
ARG_PARSER.add_argument("--debug", help="Enable debug mode", action='store_true')


def get_command_args(args: list[str] = None) -> argparse.Namespace:
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
    with open(config_file_path) as f:
        file_content = yaml.safe_load(f)

    parsed = AppConfigs.parse_obj(file_content["app"])
    global CONFIG
    CONFIG = parsed


def configure_debug_mode(args: argparse.Namespace = None):
    if not args:
        args = get_command_args()
    if args.debug:
        global CONFIG
        CONFIG.debug_mode = True
        CONFIG.log_level = "DEBUG"
