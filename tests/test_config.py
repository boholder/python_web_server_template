import os.path

from app import config


def test_command_args_parsing(tmp_path, gen_config_file):
    config_file = gen_config_file({})

    args = config.get_command_args(["-c", str(config_file), "--debug"])

    assert args.config == config_file
    assert args.debug is True


def test_config_file_loading(tmp_path, gen_config_file):
    # this directory is not created by the test logic
    log_dir = tmp_path.joinpath("log_dir")
    log_file_path = log_dir.joinpath("app.log")
    log_format = "%(message)s"

    config_file = gen_config_file(
        {"app": {"log_level": "ERROR", "log_file_path": str(log_file_path), "log_format": log_format}}
    )

    config.configure_app_with(config_file)

    assert config.CONFIG.log_level == "ERROR"
    # check if log_dir is created automatically
    assert os.path.isdir(log_dir)
    # check if log_file_path is transformed to absolute
    assert config.CONFIG.log_file_path == log_file_path.absolute()
    assert config.CONFIG.log_format == log_format


def test_debug_mode(tmp_path, gen_config_file):
    args = config.get_command_args(["--debug"])
    config.configure_debug_mode(args)
    assert config.CONFIG.debug_mode is True
