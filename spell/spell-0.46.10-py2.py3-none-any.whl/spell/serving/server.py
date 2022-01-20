import logging
from pathlib import Path
from typing import Any, Dict, Optional

from prometheus_client import (
    CollectorRegistry as PrometheusCollectorRegistry,
    multiprocess as prometheus_multiprocess,
    make_asgi_app as _make_user_metrics_app,
)

from starlette.applications import Starlette
from starlette.exceptions import ExceptionMiddleware
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.routing import Mount
from starlette.types import ASGIApp
import yaml

from spell.serving import settings
from spell.serving.api import BatchedAPI, API
from spell.serving.log import create_logging_config, get_loggers
from spell.serving.exceptions import InvalidServerConfiguration

READY_FILE = "/ready"

logger, error_logger = get_loggers("server")


def get_config(path: Optional[Path]) -> Dict[str, Any]:
    if path is None:
        return {}
    if not path.is_file():
        raise InvalidServerConfiguration("Config file must be a file")
    try:
        with path.open() as f:
            return yaml.safe_load(f)
    except yaml.scanner.ScannerError as e:
        raise InvalidServerConfiguration("Could not read config file") from e


def make_api() -> API:
    config = get_config(settings.CONFIG_FILE)
    api_class = BatchedAPI if settings.USE_BATCH_PREDICT else API
    api = api_class.from_settings()
    api.initialize_predictor(config)
    return api


def make_user_metrics_app() -> ASGIApp:
    registry = PrometheusCollectorRegistry()
    prometheus_multiprocess.MultiProcessCollector(registry)
    return _make_user_metrics_app(registry)


def create_ready_file() -> None:
    if not settings.LOCAL:
        open(READY_FILE, "a").close()


def print_config() -> None:
    logger.debug(f"Using server configuration:\n{settings.config}")


def setup_logger() -> None:
    logging.config.dictConfig(create_logging_config("server"))
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
        error_logger.setLevel(logging.DEBUG)


def make_app(api: Optional[API] = None, debug: bool = False) -> Starlette:
    if not api:
        api = make_api()
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
        Middleware(ExceptionMiddleware),
        Middleware(GZipMiddleware),
    ]
    routes = api.get_routes()
    if not settings.LOCAL:
        routes.append(Mount("/metrics", make_user_metrics_app()))
    return Starlette(
        debug=debug,
        routes=routes,
        middleware=middleware,
        on_startup=[setup_logger, print_config, create_ready_file],
    )
