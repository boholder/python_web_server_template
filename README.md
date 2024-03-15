# python_web_server_template

## Branches

This project is mainly for my own use, but I'll leave separate branches for different features.
The `main` branch contains all features.
The `basic` branch contains only early configuration, logging, ci code.

## Configuration

For all available configuration see [AppConfigs](/app/config/__init__.py) class.

## Logging

This project uses Python `logging` library for logging.
It [configures](/app/__main__.py) uvicorn loggers for a uniform logging format and save logs to file.

It [adds](/app/config/log_config.py) a [RotateFileHandler](https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler) for log persistence,
and registers this handler to the uvicorn loggers (through configuring `uvicorn.config.LOGGING_CONFIG`) and custom loggers (through `logging.basicConfig()`).
Please [note](/app/config/log_config.py) that this project reuses the file handler that uvicorn created in a tricky way,
and use it on its own logging configuration,
by this way we can avoid creating two file logging handlers for one same file.

The default log file path is `./app.log`, you can change it in the config file with `app.log_file_path` option.

This project also [uses](/app/config/log_config.py) [asgi-correlation-id](https://github.com/snok/asgi-correlation-id) middleware
for using X-Request-ID HTTP header or self-generated uuid as trace id of requests and show it in logs.

## CI

This project uses [pre-commit](https://pre-commit.com/) to run linters (ruff) and formatters (pyupgrade, ruff-format, codespell),
for more details see [.pre-commit-config.yaml](.pre-commit-config.yaml).

There are few pre-defined [development scripts](pyproject.toml) under `[tool.pdm.scripts]` section:
* `dev` - start the development server
* `lint` - run pre-commit (start linters and formatters)
* `test` - run tests
* `a` - `lint` then `test`, please constantly execute it while developing

You can build the project into executable library with `pdm build` command, then type `python app` to start it, 
or `pdm install` to install it then run it with `myapp` [console script](https://pdm-project.org/latest/reference/pep621/#console-scripts). 

## Test APIs

```shell
curl -X GET http://0.0.0.0:8000
# {"Hello":"World"}
curl -X GET http://0.0.0.0:8000/get/123?q=hi
# {"item_id":123,"q":"hi"}
curl -X POST -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"hi\",\"price\":0}" http://0.0.0.0:8000/post
# {"item_name":"hi","item_price":0.0}
```