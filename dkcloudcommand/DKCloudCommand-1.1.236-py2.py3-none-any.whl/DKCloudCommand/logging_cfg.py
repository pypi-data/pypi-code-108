from logging.config import dictConfig
from typing import Any, Dict

from DKCommon.log_utils import init_logging, InternalFilter


def configure_logging():
    init_logging()  # Setup the custom DK logging instances

    # The base logging configuration
    BASE_CONFIG: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"internal": {"()": InternalFilter}},
        "formatters": {"simple": {"format": "%(levelname)8s %(message)s - %(name)s:%(lineno)s"}},
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "filters": ["internal"],
            }
        },
        "loggers": {
            "DKCloudCommand": {"handlers": ["console"], "level": "INFO"},
            "DKCommon": {"handlers": ["console"], "level": "INFO"},
            "DKModules": {"handlers": ["console"], "level": "INFO"},
            "pymongo": {"handlers": ["console"], "level": "ERROR"},
            "urllib3": {"handlers": ["console"], "level": "ERROR"},
            "requests": {"handlers": ["console"], "level": "ERROR"},
        },
    }

    # Setup the loggers
    dictConfig(BASE_CONFIG)
