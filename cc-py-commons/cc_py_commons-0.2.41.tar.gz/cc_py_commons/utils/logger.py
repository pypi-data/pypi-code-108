import os, sys, json
import logging
import socket
from logging import StreamHandler
from logging.handlers import SysLogHandler

from cc_py_commons.config.env import env_name, app_config

class ContextFilter(logging.Filter):
  hostname = socket.gethostname()

  def filter(self, record):
    record.hostname = ContextFilter.hostname
    return True

def _config_logger():
  logger = logging.getLogger(app_config.LOG_APP_NAME)
  logger.setLevel(app_config.LOG_LEVEL)

  contextFilter = ContextFilter()
  logger.addFilter(contextFilter)
  formatter = logging.Formatter('{}: %(levelname)s %(message)s'.format(app_config.LOG_APP_NAME),
                            datefmt='%Y-%m-%d %I:%M:%S %p')

  if env_name == 'local':
    syslog = StreamHandler()
  else:
    syslog = SysLogHandler(address=('logs3.papertrailapp.com', 10024))

  syslog.setFormatter(formatter)
  logger.addHandler(syslog)
  return logger

logger = _config_logger()
