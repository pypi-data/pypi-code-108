import logging
import aiotask_context as context


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = context.get("x-ms-request-id") or ""
        except (ValueError, AttributeError):
            record.request_id = ""
        return True


LOG_SETTINGS = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "filters": ["requestid"],
        },
    },
    "filters": {
        "requestid": {
            "()": RequestIdFilter,
        },
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s - [%(levelname)s] %(module)s::%(funcName)s():l%(lineno)d %(request_id)s | %(message)s",
        },
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["console"], "propagate": True},
    },
}
