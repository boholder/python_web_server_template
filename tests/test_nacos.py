import nacos_sdk_rust_binding_py as nacos_client
import pytest

from app import config, nacos

DEFAULT_APP_CONFIG = config.AppConfigs()
DEFAULT_NACOS_CONFIG = config.NacosConfigs(server_addr="", enable_auth=True)


def test_build_nacos_client(configure_with, mock_nacos_client):
    server_addr = "1.1.1.1"
    configure_with({"app": {"enable_nacos": True}, "nacos": {"server_addr": server_addr}})

    nacos.build_nacos_client()

    actual_options: nacos_client.ClientOptions = mock_nacos_client.call_args[0][0]
    # Assert initializing with default config values
    # since they're not set in config file
    assert actual_options.server_addr == server_addr
    assert actual_options.namespace == DEFAULT_NACOS_CONFIG.namespace
    assert actual_options.app_name == DEFAULT_APP_CONFIG.name
    assert actual_options.username is None
    assert actual_options.password is None


def test_build_nacos_client_with_default_username_and_password(configure_with, mock_nacos_client):
    configure_with({"app": {"enable_nacos": True}, "nacos": {"server_addr": "", "enable_auth": True}})

    nacos.build_nacos_client()

    actual_options: nacos_client.ClientOptions = mock_nacos_client.call_args[0][0]
    assert actual_options.username == DEFAULT_NACOS_CONFIG.username
    assert actual_options.password == DEFAULT_NACOS_CONFIG.password


def test_build_service_instance(configure_with):
    configure_with({"app": {"enable_nacos": True}, "nacos": {"server_addr": "", "enable_auth": True}})

    nacos.build_nacos_service_instance()

    assert nacos._NACOS_SERVICE_INSTANCE.ip == DEFAULT_APP_CONFIG.outer_host
    assert nacos._NACOS_SERVICE_INSTANCE.port == DEFAULT_APP_CONFIG.outer_port


@pytest.mark.asyncio(scope="function")
async def test_register_onto_nacos(configure_with, mock_nacos_client):
    configure_with({"app": {"enable_nacos": True}, "nacos": {"server_addr": "", "enable_auth": True}})

    await nacos.register_onto_nacos()

    actual_kwargs = mock_nacos_client.register_instance.call_args.kwargs
    assert actual_kwargs["service_name"] == DEFAULT_APP_CONFIG.name
    assert actual_kwargs["group"] == DEFAULT_NACOS_CONFIG.group
