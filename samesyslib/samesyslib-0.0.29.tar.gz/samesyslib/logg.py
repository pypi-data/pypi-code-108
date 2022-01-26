import os
import logging.config
import structlog
try:
    import gunicorn_cfg as gcfg
except ImportError:
    class GcfgObject(object):
        pass
    gcfg = GcfgObject()
    gcfg.strctlog_file = 'structlog.log'

# proudly copied from https://gist.github.com/airhorns/c2d34b2c823541fc0b32e5c853aab7e7

timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True, key='@timestamp')
pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry is not from structlog.
    structlog.stdlib.add_log_level,
    timestamper,
]

handlers = ['development'] if int(os.getenv('DEBUG', 1)) else ['file', 'development']
log_dict_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
                "foreign_pre_chain": pre_chain,
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": pre_chain
            },
        },
        "handlers": {
            "development": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "console"},
            "file": {
                "level": "DEBUG",
                'class': 'logging.FileHandler',
                'filename': gcfg.strctlog_file,
                "formatter": "json"
            },
        },
        "loggers": {
            "": {
                "handlers": handlers,
                "level": "DEBUG",
                "propagate": True,
            },
        }
}

logging.config.dictConfig(log_dict_config)


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


class GunicornLogger(object):
    """
    A stripped down version of https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py to provide structlog logging in gunicorn
    Modified from http://stevetarver.github.io/2017/05/10/python-falcon-logging.html

    Usage gunicorn -c ../gunicorn_cfg_django.py wsgi:application --logger-class samesyslib.logg.GunicornLogger

    """

    def __init__(self, cfg):
        self._error_logger = structlog.get_logger("gunicorn.error")
        self._error_logger.setLevel(logging.INFO)
        self._access_logger = structlog.get_logger("gunicorn.access")
        self._access_logger.setLevel(logging.INFO)
        self.cfg = cfg

    def critical(self, msg, *args, **kwargs) -> None:
        self._error_logger.error(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        self._error_logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        self._error_logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        self._error_logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs) -> None:
        self._error_logger.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs) -> None:
        self._error_logger.exception(msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs) -> None:
        self._error_logger.log(lvl, msg, *args, **kwargs)

    def access(self, resp, req, environ, request_time) -> None:
        status = resp.status
        if isinstance(status, str):
            status = status.split(None, 1)[0]

        self._access_logger.info(
            "request",
            method=environ["REQUEST_METHOD"],
            request_uri=environ["RAW_URI"],
            status=status,
            response_length=getattr(resp, "sent", None),
            request_time_seconds="%d.%06d" % (request_time.seconds, request_time.microseconds),
            pid="<%s>" % os.getpid(),
        )

    def reopen_files(self) -> None:
        pass  # we don't support files

    def close_on_exec(self) -> None:
        pass  # we don't support files
