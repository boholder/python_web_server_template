from app import config


def test_command_args_parsing(tmp_path, gen_config_file):
    config_file = gen_config_file({})

    args = config.get_command_args(["-c", str(config_file),
                                    "--debug"])

    assert str(args.config) == str(config_file)
    assert args.debug is True


def test_config_file_loading(tmp_path, gen_config_file):
    config_file = gen_config_file({"app": {"log_level": "ERROR"}})
    config.configure_app_with(config_file)
    assert config.CONFIG.log_level == "ERROR"


def test_debug_mode(tmp_path, gen_config_file):
    args = config.get_command_args(["--debug"])
    config.configure_debug_mode(args)
    assert config.CONFIG.debug_mode is True
