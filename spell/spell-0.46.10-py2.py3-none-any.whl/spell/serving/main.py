import logging
import multiprocessing
import shlex
from typing import Callable, Optional

from gunicorn.app.base import Application

from spell.serving import settings as server_settings
from spell.serving.proxy import settings as proxy_settings
from prometheus_client import multiprocess as prometheus_multiprocess


def post_worker_init(log_prefix: str) -> Callable:
    formatter = logging.Formatter(f"{log_prefix} %(message)s")

    def hook(worker):
        logger = logging.getLogger("uvicorn.access")
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(formatter)

    return hook


def child_exit(server, worker):
    # apps using the prometheus metrics client need to clear out their cache for the killed worker process.
    prometheus_multiprocess.mark_process_dead(worker.pid)


class GunicornApplication(Application):
    def __init__(self, additional_settings="", log_prefix="", options=None):
        self.options = options or {}
        self.additional_settings = additional_settings
        super().__init__()

    def load_config(self) -> None:
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}

        # First load the default configuration
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

        # Override anything from the GUNICORN_ENV_ARGS environment variable
        parser = self.cfg.parser()
        env_args = parser.parse_args(self.cfg.get_cmd_args_from_env())
        for k, v in vars(env_args).items():
            if v is None or k == "args":
                continue
            self.cfg.set(k.lower(), v)

        # Lastly, update the configuration with any command line settings.
        cli_args = parser.parse_args(shlex.split(self.additional_settings))
        for k, v in vars(cli_args).items():
            if v is None or k == "args":
                continue
            self.cfg.set(k.lower(), v)

        # current directory might be changed by the config now
        # set up import paths and follow symlinks
        self.chdir()


class ProxyApplication(GunicornApplication):
    DEFAULT_OPTIONS = {
        "bind": "0.0.0.0:8000",
        "workers": 1,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "accesslog": "-",
        "proc_name": "proxy",
        "errorlog": "-",
        "loglevel": "info",
        "capture_output": True,
        "post_worker_init": post_worker_init(""),
    }

    def load(self):
        from spell.serving.proxy.proxy import make_app

        return make_app()

    @classmethod
    def from_settings(cls, additional_settings: str = ""):
        options = cls.DEFAULT_OPTIONS
        if proxy_settings.DEBUG:
            options["loglevel"] = "debug"
            options["post_worker_init"] = post_worker_init("[proxy]")
        return cls(additional_settings=additional_settings, options=options)


class ServerApplication(GunicornApplication):
    DEFAULT_OPTIONS = {
        "bind": "0.0.0.0:8000",
        "workers": (multiprocessing.cpu_count() * 2) + 1,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "proc_name": "server",
        "errorlog": "-",
        "loglevel": "info",
        "capture_output": True,
        "child_exit": child_exit,
    }

    def load(self):
        from spell.serving.server import make_app

        return make_app(debug=server_settings.DEBUG)

    @staticmethod
    def get_access_log_prefix(num_workers: int) -> str:
        prefix = ""
        if server_settings.DEBUG or num_workers is None or num_workers > 1:
            prefix = "[server"
            if num_workers != 1:
                prefix += " %(process)d"
            prefix += "]"
        return prefix

    @classmethod
    def from_settings(cls, additional_settings: str = "", num_workers: Optional[int] = None):
        options = cls.DEFAULT_OPTIONS
        if num_workers:
            options["workers"] = num_workers
        if server_settings.USE_BATCH_PREDICT:
            if proxy_settings.MODEL_SERVER_SOCKET:
                options["bind"] = f"unix:{proxy_settings.MODEL_SERVER_SOCKET}"
            else:
                options["bind"] = "localhost:5000"
        if server_settings.DEBUG:
            options["loglevel"] = "debug"
        if server_settings.DEBUG or not server_settings.USE_BATCH_PREDICT:
            options["accesslog"] = "-"
            options["post_worker_init"] = post_worker_init(cls.get_access_log_prefix(num_workers))
        return cls(additional_settings=additional_settings, options=options)


def run_proxy(additional_settings: str = "") -> None:
    ProxyApplication.from_settings(additional_settings=additional_settings).run()


def run_servers(
    num_workers: Optional[int] = None,
    additional_settings: str = "",
) -> None:
    ServerApplication.from_settings(additional_settings=additional_settings, num_workers=num_workers).run()


def main(
    num_server_workers: Optional[int] = None,
    additional_server_settings: str = "",
    additional_proxy_settings: str = "",
):
    if server_settings.USE_BATCH_PREDICT:
        server_process = multiprocessing.Process(
            target=run_servers,
            args=(num_server_workers, additional_server_settings),
            daemon=True,
        )
        server_process.start()
        run_proxy(additional_settings=additional_proxy_settings)
    else:
        run_servers(num_server_workers, additional_server_settings)
