import asyncio
import logging

import nacos_sdk_rust_binding_py as nacos

from app import config

_NACOS_CLIENT: nacos.NacosNamingClient
_NACOS_SERVICE_INSTANCE: nacos.NacosServiceInstance

log = logging.getLogger(__name__)


async def initialize_nacos():
    # Note that this method won't be tested,
    # because Mock and MagicMock is not supported by pickle when running multiprocessing code
    # ref: https://github.com/python/cpython/issues/100090
    build_nacos_client()
    build_nacos_service_instance()
    await asyncio.get_event_loop().run_in_executor(
        config.PROCESS_EXECUTOR, register, _NACOS_CLIENT, _NACOS_SERVICE_INSTANCE
    )


def register(client: nacos.NacosNamingClient = None, service_instance: nacos.NacosServiceInstance = None):
    if client is None:
        client = _NACOS_CLIENT
    if service_instance is None:
        service_instance = _NACOS_SERVICE_INSTANCE

    try:
        client.register_instance(
            service_name=config.CONFIG.app.name,
            group=config.CONFIG.nacos.group,
            service_instance=service_instance,
        )
    except Exception as e:
        log.error("Failed to register onto nacos", exc_info=e)
    else:
        log.info("Successfully registered onto nacos")


def build_nacos_client():
    global _NACOS_CLIENT
    _NACOS_CLIENT = nacos.NacosNamingClient(
        nacos.ClientOptions(
            server_addr=config.CONFIG.nacos.server_addr,
            namespace=config.CONFIG.nacos.namespace,
            app_name=config.CONFIG.app.name,
            username=config.CONFIG.nacos.username,
            password=config.CONFIG.nacos.password,
        )
    )
    log.debug(f"Nacos client: {_NACOS_CLIENT}")


def build_nacos_service_instance():
    global _NACOS_SERVICE_INSTANCE
    _NACOS_SERVICE_INSTANCE = nacos.NacosServiceInstance(
        ip=config.CONFIG.app.outer_host, port=config.CONFIG.app.outer_port
    )
