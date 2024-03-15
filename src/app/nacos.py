import logging

import nacos_sdk_rust_binding_py as nacos

from app import config

_NACOS_CLIENT: nacos.NacosNamingClient
_NACOS_SERVICE_INSTANCE: nacos.NacosServiceInstance

log = logging.getLogger(__name__)


async def register_onto_nacos():
    build_nacos_client()
    build_nacos_service_instance()

    _NACOS_CLIENT.register_instance(
        service_name=config.CONFIG.app.name, group=config.CONFIG.nacos.group, service_instance=_NACOS_SERVICE_INSTANCE
    )
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
