import datetime
import os
from logging import *
import logging.config

from .ding_alarm import ding_alarm
from .filter import HostAddressFilter, RequestAddressFilter, ConcurrentIdFilter, NameFilter
from .weather import weather_report
from ..config.config_client import ConfigClient

__all__ = ["logging"]

# new logging level REPORT
REPORT = 100
logging.addLevelName(REPORT, "REPORT")
log_dir = "/data/log/flask/"
LIB_APP_ID = "winhye_common"


def logger_report(self, msg: str, weather: bool = False, *args, **kwargs):
    """
    Report level for logger, support report weather

    :param msg: dict, report content
    :param weather: bool, report to whether, default is False
    """
    if self.isEnabledFor(REPORT):
        self._log(REPORT, msg, args, **kwargs)
    if weather is True:
        weather_report()


def error(self, msg: str, is_alarm: bool = True, *args, **kwargs):
    """
    Report error for logger, support report alarm

    :param msg: dict, error content
    :param is_alarm: bool, report to alarm, default is True
    """
    if is_alarm:
        ding_alarm.send_alarm_message(msg)
    if self.isEnabledFor(ERROR):
        self._log(ERROR, msg, args, **kwargs)


logging.Logger.report = logger_report
logging.Logger.error = error

app_id = os.environ.get("APP_ID", "NOT_EXIST")
if app_id == "NOT_EXIST":
    app_id = LIB_APP_ID
ConfigClient.init(app_id)
log_conf = ConfigClient.get_configger("winhye_software.common")
log_config = log_conf.get_group("log_level")

# 是否禁用第三方日志(用户名不为当前用户名)
filter_list = ["hostname", "source_ip", "concurrent_id"]
if eval(log_config.third_log):
    filter_list.append("name")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "winhye": {
            "format": "[%(asctime)s] <host=%(hostname)s source=%(source_ip)s> %(filename)s line:%(lineno)d <process=%(process)d concurrent=%(concurrent_id)d> [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "filters": {
        "hostname": {
            "()": HostAddressFilter
        },
        "source_ip": {
            "()": RequestAddressFilter
        },
        "concurrent_id": {
            "()": ConcurrentIdFilter
        },
        "name": {
            "()": NameFilter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_config.console,
            "formatter": "winhye",
            "filters": filter_list
        },
        "file": {
            'level': log_config.file,
            "class": "winhye_common.winhye_handlers.file_handler.MultiprocessHandler",
            "filename": os.path.join(log_dir, "log.log"),
            "formatter": "winhye",
            "filters": filter_list,
            "when": "H",
            "backupCount": 168
        }
    },
    "loggers": {
        "": {
            "level": "DEBUG",  # logger日志输出级别
            "handlers": ["console", "file"],
            'propagate': True
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": True,
            "qualname": "gunicorn.error"
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": True,
            "qualname": "gunicorn.access"
        },
    }
}

# 新建log目录
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.config.dictConfig(logging_config)
