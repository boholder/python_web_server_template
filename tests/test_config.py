import os.path

from app import config


def test_command_args_parsing(tmp_path, gen_config_file):
    config_file = gen_config_file({})

    args = config.get_command_args(["-c", str(config_file), "--debug"])

    assert args.config == config_file
    assert args.debug is True


def test_debug_mode(tmp_path, gen_config_file):
    args = config.get_command_args(["--debug"])
    config.configure_debug_mode(args)
    assert config.CONFIG.app.debug_mode is True
    assert config.CONFIG.app.log_level == "DEBUG"


def test_loading_app_configs_from_config_file(tmp_path, gen_config_file):
    # this directory is not created by the test logic
    log_dir = tmp_path.joinpath("log_dir")
    log_file_path = log_dir.joinpath("app.log")
    log_format = "%(message)s"
    host = "1.1.1.1"
    port = 1111

    config_file = gen_config_file(
        {
            "app": {
                "name": "app",
                "log_level": "ERROR",
                "log_file_path": str(log_file_path),
                "log_format": log_format,
                "host": host,
                "port": port,
            }
        }
    )

    config.configure_app_with(config_file)

    assert config.CONFIG.app.name == "app"
    assert config.CONFIG.app.log_level == "ERROR"
    # check if log_dir is created automatically
    assert os.path.isdir(log_dir)
    # check if log_file_path is transformed to absolute
    assert config.CONFIG.app.log_file_path == log_file_path.absolute()
    assert config.CONFIG.app.log_format == log_format
    assert config.CONFIG.app.host == host
    assert config.CONFIG.app.port == port

    assert config.CONFIG.nacos is None


def test_not_load_nacos_config_if_not_enabled(tmp_path, gen_config_file):
    config_file = gen_config_file({"app": {"enable_nacos": False}, "nacos": {}})

    config.configure_app_with(config_file)

    assert config.CONFIG.nacos is None


def test_not_load_nacos_auth_config_if_not_enabled(tmp_path, gen_config_file):
    username = "user"
    password = "pwd"
    config_file = gen_config_file(
        {
            "app": {"enable_nacos": True},
            "nacos": {"enable_auth": False, "server_addr": "", "username": username, "password": password},
        }
    )

    config.configure_app_with(config_file)

    assert config.CONFIG.nacos.enable_auth is False
    assert config.CONFIG.nacos.username is None
    assert config.CONFIG.nacos.password is None


def test_load_nacos_configs_from_config_file(tmp_path, gen_config_file):
    server_addr = "127.0.0.1:8848"
    enable_auth = True
    username = "user"
    password = "pwd"
    namespace = "ns"
    group = "grp"
    config_file = gen_config_file(
        {
            "app": {"enable_nacos": True},
            "nacos": {
                "server_addr": server_addr,
                "enable_auth": enable_auth,
                "username": username,
                "password": password,
                "namespace": namespace,
                "group": group,
            },
        }
    )

    config.configure_app_with(config_file)

    assert config.CONFIG.nacos.server_addr == server_addr
    assert config.CONFIG.nacos.enable_auth == enable_auth
    assert config.CONFIG.nacos.username == username
    assert config.CONFIG.nacos.password == password
    assert config.CONFIG.nacos.namespace == namespace
    assert config.CONFIG.nacos.group == group
