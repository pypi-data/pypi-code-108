import logging
from typing import Any, Dict, Tuple


def create_logging_config(proc_name: str) -> Dict[str, Any]:
    return dict(
        version=1,
        disable_existing_loggers=False,
        root={"level": "INFO", "handlers": ["console"]},
        loggers={
            f"spell.serving.{proc_name}.error": {
                "level": "WARNING",
                "handlers": ["error_console"],
                "propagate": True,
                "qualname": f"spell.serving.{proc_name}.error",
            },
            f"spell.serving.{proc_name}": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": True,
                "qualname": f"spell.serving.{proc_name}",
            },
        },
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": "ext://sys.stdout",
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": "ext://sys.stderr",
            },
        },
        formatters={
            "generic": {
                "format": f"[%(asctime)s] [{proc_name} %(process)d] [%(levelname)s] %(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
                "class": "logging.Formatter",
            }
        },
    )


def get_loggers(proc_name: str) -> Tuple[logging.Logger, logging.Logger]:
    logger = logging.getLogger(f"spell.serving.{proc_name}")
    error_logger = logging.getLogger(f"spell.serving.{proc_name}.error")
    return logger, error_logger
