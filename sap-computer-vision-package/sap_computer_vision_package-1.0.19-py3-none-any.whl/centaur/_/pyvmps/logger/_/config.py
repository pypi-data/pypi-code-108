import sys
from typing import Dict

from centaur._.pyvmps.cfg.config import EnvVarGoPyCommon

LOG_LEVEL = EnvVarGoPyCommon.LOG_LEVEL

# fmt: off
logging_config: Dict = {
    "version": 1,
    "incremental": False,
    "disable_existing_loggers": False,
    "root": {
        "level": LOG_LEVEL,
        "handlers": [
            "console"
        ]
    },
    "filters": {
        "example": {
            "()": "centaur._.pyvmps.logger._.filters.ExampleFilter"
        }
    },
    "formatters": {
        "plain": {
            "format": "%(asctime)s %(levelname)-8s %(name)s %(message)s"
        },
        "colorized": {
            "()": "centaur._.pyvmps.logger._.formatters.ColorizedFormatter"
        },
        "custom": {
            "format": "%(asctime)s|%(levelname)s|%(name)s|%(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "filters": [
                "example"
            ],
            "formatter": "colorized",
            "stream": sys.stdout
        },
        "console2": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "custom",
            "stream": sys.stdout
        }
    }
}
