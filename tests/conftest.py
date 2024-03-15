import pytest
import yaml

from app import config


@pytest.fixture
def gen_config_file(tmp_path):
    """Generate a temp config file for testing."""

    def wrapper(content: dict):
        file_path = tmp_path.joinpath("test_config.yaml")
        yaml.safe_dump(content, file_path.open("w", encoding="utf-8"))
        return file_path

    return wrapper


@pytest.fixture
def configure_with(gen_config_file):
    """Configure the app with the given config."""

    def wrapper(content: dict):
        f = gen_config_file(content)
        config.configure_app_with(f)

    return wrapper
