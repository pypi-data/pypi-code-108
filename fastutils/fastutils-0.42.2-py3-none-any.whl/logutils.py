"""
Make logging setup easy. Default logging settings:

```
logging_config = {
   "version": 1,
   "disable_existing_loggers": False,
   "formatters": {
      "default": {
            "format": "{asctime} {levelname} {pathname} {lineno} {module} {funcName} {process} {thread} {message}",
            "style": "{"
      },
      "message_only": {
            "format": "{message}",
            "style": "{",
      },
      "json": {
            "class": "jsonformatter.JsonFormatter",
            "format": {
               "asctime": "asctime",
               "levelname": "levelname",
               "pathname": "pathname",
               "lineno": "lineno",
               "module": "module",
               "funcName": "funcName",
               "process": "process",
               "thread": "thread",
               "message": "message",
            },
      },
   },
   "handlers": {
      "default_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
      },
      "default_file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": logfile,
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "default",
      },
      "json_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
      },
      "json_file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": logfile,
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "json",
      },
   },
   "loggers": {
   },
   "root": {
      "handlers": ["default_file", "default_console"],
      "level": loglevel,
      "propagate": True,
   }
}
```

Example:

```
from fastutils import logutils

def setup(settings):
    logging_settings = settings.get("logging", {})
    logutils.setup(**logging_settings)

```
"""
import os
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler

from jsonformatter import JsonFormatter
from . import dictutils

file_handler_backupCount = 30

def get_console_handler(formatter:str = "default", loglevel:str="DEBUG") -> dict:
    """Make a console handler settings.
    """
    return {
        "level": loglevel,
        "class": ".".join([StreamHandler.__module__, StreamHandler.__name__]),
        "formatter": formatter,
    }

def get_file_handler(filename:str, formatter:str="default", loglevel:str="DEBUG") -> dict:
    """Make a file handler settings.
    """
    return  {
        "level": loglevel,
        "class": ".".join([TimedRotatingFileHandler.__module__, TimedRotatingFileHandler.__name__]),
        "filename": filename,
        "when": "midnight",
        "interval": 1,
        "backupCount": file_handler_backupCount,
        "formatter": formatter,
        "encoding": "utf-8",
    }

def get_simple_config(logfile:str=None, loglevel:str=None, logfmt:str=None, loggers:dict=None, logging:dict=None, **kwargs) -> dict:
    """Make simple logging settings.

    logfile default to app.log.
    loglevel choices are: DEBUG/INFO/WARNING/ERROR. default to INFO.
    logfmt choices are: default/message_only/json. default to default.
    Use logger parameter to override the default settings' logger sections.
    Use logging parameter to override the whole settings.

    """
    loggers = loggers or {}
    config = logging or {}
    logfile = logfile or config.get("logfile", "app.log")
    loglevel = loglevel or config.get("loglevel", "INFO")
    logfmt = logfmt or config.get("logfmt", "default")
    # make sure log folder exists...
    logfolder = os.path.abspath(os.path.dirname(logfile))
    if not os.path.exists(logfolder):
        os.makedirs(logfolder, exist_ok=True)
    # default logging template
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "{asctime} {levelname} {pathname} {lineno} {module} {funcName} {process} {thread} {message}",
                "style": "{"
            },
            "message_only": {
                "format": "{message}",
                "style": "{",
            },
            "json": {
                "class": ".".join([JsonFormatter.__module__, JsonFormatter.__name__]),
                "format": {
                    "asctime": "asctime",
                    "levelname": "levelname",
                    "pathname": "pathname",
                    "lineno": "lineno",
                    "module": "module",
                    "funcName": "funcName",
                    "process": "process",
                    "thread": "thread",
                    "message": "message",
                },
            },
        },
        "handlers": {
            "default_console": get_console_handler("default", "DEBUG"),
            "default_file": get_file_handler(logfile, "default", "DEBUG"),
            "json_console": get_console_handler("json", "DEBUG"),
            "json_file": get_file_handler(logfile, "json", "DEBUG"),
            "message_only_console": get_console_handler("message_only", "DEBUG"),
            "message_only_file": get_file_handler(logfile, "message_only", "DEBUG"),
        },
        "loggers": {
        },
        "root": {
            "handlers": [logfmt+"_file", logfmt+"_console"],
            "level": loglevel,
            "propagate": True,
        }
    }
    dictutils.deep_merge(logging_config, config)
    dictutils.deep_merge(logging_config, {"loggers": loggers})
    dictutils.deep_merge(logging_config, kwargs)
    return logging_config

def setup(*args, **kwargs):
    """Using get_simple_config to get the logging settings and enable them. Parameters are the same with get_simple_config function.
    """
    config = get_simple_config(*args, **kwargs)
    dictConfig(config)
