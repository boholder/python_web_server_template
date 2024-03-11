from app import config


def test_command_args_parsing(tmp_path, gen_config_file):
    config_file = gen_config_file({})

    args = config.get_command_args(["-c", str(config_file),
                                    "--debug"])

    assert str(args.config) == str(config_file)
    assert args.debug is True
