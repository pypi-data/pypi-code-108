import sys
import logging
import logging.config


# Logging format example:
# 2018/11/20 12:36:37 INFO databricks_registry_webhooks: Creating new webhook
LOGGING_LINE_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
LOGGING_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"


def _configure_loggers(root_module_name):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "databricks_registry_webhooks_formatter": {
                    "format": LOGGING_LINE_FORMAT,
                    "datefmt": LOGGING_DATETIME_FORMAT,
                },
            },
            "handlers": {
                "databricks_registry_webhooks_handler": {
                    "level": "INFO",
                    "formatter": "databricks_registry_webhooks_formatter",
                    "class": "logging.StreamHandler",
                    "stream": sys.stderr,
                },
            },
            "loggers": {
                root_module_name: {
                    "handlers": ["databricks_registry_webhooks_handler"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )
