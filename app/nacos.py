import logging

import nacos_sdk_rust_binding_py as nacos

_APP_NAME = "app_py"
_GROUP = "DEFAULT_GROUP"
_OPTIONS = nacos.ClientOptions(
    server_addr="127.0.0.1:8848", namespace="public", app_name=_APP_NAME, username="nacos", password="nacos"
)
_NACOS_CLIENT: nacos.NacosNamingClient
_NACOS_SERVICE_INSTANCE: nacos.NacosServiceInstance

log = logging.getLogger(__name__)


def register_onto_nacos():
    global _NACOS_CLIENT
    _NACOS_CLIENT = nacos.NacosNamingClient(_OPTIONS)
    global _NACOS_SERVICE_INSTANCE
    _NACOS_SERVICE_INSTANCE = nacos.NacosServiceInstance(ip="127.0.0.1", port=8080)

    _NACOS_CLIENT.register_instance(service_name=_APP_NAME, group=_GROUP, service_instance=_NACOS_SERVICE_INSTANCE)
    log.info("Registered onto nacos successfully")
