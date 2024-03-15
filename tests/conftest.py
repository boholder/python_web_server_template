from unittest.mock import MagicMock

import pytest
import yaml

from app import config, nacos


@pytest.fixture
def gen_config_file(tmp_path):
    """Generate a temp config file for testing."""

    def wrapper(content: dict):
        file_path = tmp_path.joinpath("test_config.yaml")
        yaml.safe_dump(content, file_path.open("w", encoding="utf-8"))
        return file_path

    return wrapper


@pytest.fixture
def configure_with():
    """Configure the app with the given config."""

    def wrapper(content: dict):
        config.configure_app_with(content)

    return wrapper


@pytest.fixture
def mock_nacos_client_with_config(monkeypatch, configure_with):
    """
    Mock the NacosNamingClient then we don't need to actually connect to the nacos server.
    """

    mock_client = MagicMock()
    mock_client.return_value = mock_client
    monkeypatch.setattr("nacos_sdk_rust_binding_py.NacosNamingClient", mock_client)

    def wrapper(content: dict):
        """

        :param content: test configuration
        :return: mock client
        """

        configure_with(content)
        nacos.build_nacos_client()
        nacos.build_nacos_service_instance()
        return mock_client

    return wrapper
