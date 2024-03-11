import pytest
import yaml


@pytest.fixture
def gen_config_file(tmp_path):
    """Generate a temp config file for testing."""

    def wrapper(content: dict):
        file_path = tmp_path.joinpath("test_config.yaml")
        yaml.safe_dump(content, file_path.open("w", encoding="utf-8"))
        return file_path

    return wrapper
