import logging

import nacos_sdk_rust_binding_py as nacos_sdk

from app import config

_NACOS_CLIENT: nacos_sdk.AsyncNacosNamingClient
_NACOS_SERVICE_INSTANCE: nacos_sdk.NacosServiceInstance

log = logging.getLogger(__name__)


async def initialize_nacos():
    # Note that this method won't be tested,
    # because Mock and MagicMock is not supported by pickle when running multiprocessing code
    # ref: https://github.com/python/cpython/issues/100090
    build_nacos_client()
    build_nacos_service_instance()
    await register()


async def register():
    try:
        await _NACOS_CLIENT.register_instance(
            service_name=config.CONFIG.app.name,
            group=config.CONFIG.nacos.group,
            service_instance=_NACOS_SERVICE_INSTANCE,
        )
    except Exception as e:
        log.error("Failed to register onto nacos", exc_info=e)
    else:
        log.info("Successfully registered onto nacos")


def build_nacos_client():
    global _NACOS_CLIENT
    _NACOS_CLIENT = nacos_sdk.AsyncNacosNamingClient(
        nacos_sdk.ClientOptions(
            server_addr=config.CONFIG.nacos.server_addr,
            namespace=config.CONFIG.nacos.namespace,
            app_name=config.CONFIG.app.name,
            username=config.CONFIG.nacos.username,
            password=config.CONFIG.nacos.password,
        )
    )


def build_nacos_service_instance():
    global _NACOS_SERVICE_INSTANCE
    _NACOS_SERVICE_INSTANCE = nacos_sdk.NacosServiceInstance(
        ip=config.CONFIG.app.outer_host, port=config.CONFIG.app.outer_port
    )
