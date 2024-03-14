import os.path

from app import config


def test_command_args_parsing(tmp_path, gen_config_file):
    config_file = gen_config_file({})

    args = config.get_command_args(["-c", str(config_file), "--debug"])

    assert args.config == config_file
    assert args.debug is True


def test_loading_app_configs_from_config_file(tmp_path, gen_config_file):
    # this directory is not created by the test logic
    log_dir = tmp_path.joinpath("log_dir")
    log_file_path = log_dir.joinpath("app.log")
    log_format = "%(message)s"
    port = 1111

    config_file = gen_config_file(
        {
            "app": {
                "name": "app",
                "log_level": "ERROR",
                "log_file_path": str(log_file_path),
                "log_format": log_format,
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
    assert config.CONFIG.app.port == port

    assert config.CONFIG.nacos is None


def test_loading_nacos_configs_from_config_file(tmp_path, gen_config_file):
    config_file = gen_config_file({"app": {"enable_nacos": True}, "nacos": {}})

    config.configure_app_with(config_file)

    assert config.CONFIG.nacos is not None


def test_debug_mode(tmp_path, gen_config_file):
    args = config.get_command_args(["--debug"])
    config.configure_debug_mode(args)
    assert config.CONFIG.app.debug_mode is True
