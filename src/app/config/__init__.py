import argparse
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator, model_validator

from .log_config import configure_app_logging, configure_uvicorn_logging


# noinspection PyNestedDecorators
# to suppress false positive on overlapping decorators
# ref: https://youtrack.jetbrains.com/issue/PY-34368
class AppConfigs(BaseModel):
    """Configuration for this application."""

    name: str = "app"
    """The application name, will be used when registering onto services"""
    host: str = "0.0.0.0"
    """The host to listen on"""
    port: int = 8000
    """The port to listen on"""
    outer_host: str = "0.0.0.0"
    """The host that outer services wound use to call this application, will be used when registering onto services"""
    outer_port: int = 8000
    """The port that outer services wound use to call this application, will be used when registering onto services"""
    log_level: str = "INFO"
    """Log level of application logs"""
    log_file_path: Path = Path("./app.log").absolute()
    """Path of ALL logs (including uvicorn)"""
    # time | log level | logger name | trace id | process id | thread id | message
    # %(levelname)8s: max 8 characters for "CRITICAL"
    # ref: https://docs.python.org/3/library/logging.html#logrecord-attributes
    log_format: str = "%(asctime)s|%(levelname)-8s|%(name)s|%(correlation_id)s|%(process)d|%(thread)d| %(message)s"
    """Log format of ALL logs (including uvicorn)"""
    debug_mode: bool = False
    """When debug_mode is on, log level is set to DEBUG, uvicorn will reload when code changes"""
    enable_nacos: bool = False
    """Enable Nacos related features"""

    # ref: https://docs.pydantic.dev/latest/concepts/validators/#field-validators
    @field_validator("log_file_path")
    @classmethod
    def post_log_file_path(cls, v: Path) -> Path:
        # Resolve path to absolute
        v = v.absolute()
        # Create parent directory if not exist
        v.parent.mkdir(exist_ok=True, parents=True)
        return v


class NacosConfigs(BaseModel):
    """Configurations for nacos client"""

    server_addr: str
    """
    The nacos server(s) address(es)
    e.g. "127.0.0.1:8848"
    the underlying "nacos-sdk-rust" library supports multiple server address since v0.2.1
    e.g. "address:port[,address:port],...]"
    ref: https://github.com/nacos-group/nacos-sdk-rust/blob/b8f0298822318beaae116fceff59f0c9fe245741/CHANGELOG.md?plain=1#L124C3-L124C51
    """
    enable_auth: bool = False
    """Set it to same as nacos server configuration"""
    username: str | None = "nacos"
    """
    username and password are used for authentication with nacos server,
    only be set to nacos client when enable_auth is True.
    "nacos" is default username/password of a new nacos server.
    """
    password: str | None = "nacos"
    namespace: str = ""
    """Leave it to "", the nacos server will register this service to default "public" namespace"""
    group: str = ""
    """Leave it to "", the nacos server will register this service to default "DEFAULT_GROUP" group"""

    # ref: https://docs.pydantic.dev/latest/concepts/validators/#model-validators
    @model_validator(mode="after")
    def remove_username_and_password_if_auth_disabled(self):
        if not self.enable_auth:
            self.username = None
            self.password = None

        return self


# noinspection PyNestedDecorators
class Configs(BaseModel):
    """Represents all configuration, provides unified access to configuration values."""

    app: AppConfigs = AppConfigs()
    # Only exists when app.enable_nacos is True
    nacos: NacosConfigs | None = None

    @field_validator("nacos", mode="before")
    @classmethod
    def parse_nacos_config_if_enabled(cls, value, values):
        if values.data["app"].enable_nacos:
            return value
        else:
            return None


# Global configuration object
# initialize with default values
# Make sure to use "config.CONFIG.xxx" to access it, so it can retrieve newly updated values
CONFIG: Configs = Configs()

_ARG_PARSER = argparse.ArgumentParser(description="Web Server")
_ARG_PARSER.add_argument("-c", "--config", help="Path of the config file", type=Path)
_ARG_PARSER.add_argument("--debug", help="Enable debug mode", action="store_true")


def get_command_args(args: list[str] | None = None) -> argparse.Namespace:
    args = sys.argv[1:] if args is None else args
    return _ARG_PARSER.parse_args(args)


def configure_app():
    args = get_command_args()

    if config_file_path := _load_config_file_if_passed(args):
        configure_app_with(config_file_path)

    configure_debug_mode(args)


def _load_config_file_if_passed(args: argparse.Namespace) -> Path | None:
    if cfg_path := args.config:
        abs_path = Path.resolve(Path(cfg_path))
        return abs_path


def configure_app_with(config_file: Path | dict):
    parsed: Configs | None = None

    if isinstance(config_file, Path):
        file_content: dict
        with open(config_file, encoding="utf-8") as f:
            file_content = yaml.safe_load(f)
            parsed = Configs.model_validate(file_content)

    elif isinstance(config_file, dict):
        parsed = Configs.model_validate(config_file)

    global CONFIG
    CONFIG = parsed


def configure_debug_mode(args: argparse.Namespace):
    if args.debug:
        global CONFIG
        CONFIG.app.debug_mode = True
        CONFIG.app.log_level = "DEBUG"


__all__ = [
    "CONFIG",
    "get_command_args",
    "configure_app",
    "configure_app_with",
    "configure_debug_mode",
    "configure_uvicorn_logging",
    "configure_app_logging",
]
