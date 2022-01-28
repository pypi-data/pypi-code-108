import logging
import sys

import structlog

from .gnista_connetion import GnistaConnection, KeyringGnistaConnection, StaticTokenGnistaConnection
from .gnista_credential_manager import GnistaCredentialManager
from .gnista_data_point import GnistaDataPoint
from .gnista_data_points import GnistaDataPoints
from .gnista_data_source import GnistaDataSource
from .gnista_data_sources import GnistaDataSources

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)


structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
