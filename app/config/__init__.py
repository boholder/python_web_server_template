import argparse
from pathlib import Path

import yaml
from pydantic import BaseModel


class AppConfigs(BaseModel):
    """Contains the configuration for this application."""

    log_level: str = "INFO"


# Global configuration object
# initialize with default values
CONFIG: AppConfigs = AppConfigs()


def configure_app():
    if config_file_path := load_config_file_if_passed():
        configure_app_with(config_file_path)


def load_config_file_if_passed() -> Path | None:
    parser = argparse.ArgumentParser(description="Web Server")
    parser.add_argument("-c", "--config", help="Path of the config file", type=Path)
    args = parser.parse_args()
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
