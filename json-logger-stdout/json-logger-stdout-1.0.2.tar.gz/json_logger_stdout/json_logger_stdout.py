import json
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger


class JSONStdFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(JSONStdFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


class JSONLoggerStdout:
    def __init__(self, loggerName=None):
        self.loggerName = loggerName

        self.logger = self.get_root_logger()

        self.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logHandler = logging.StreamHandler()
            self.formatter = JSONStdFormatter('%(timestamp)s %(level)s %(message)s')
            self.logHandler.setFormatter(self.formatter)
            self.logger.addHandler(self.logHandler)

    def get_root_logger(self):
        return logging.getLogger(self.loggerName) if self.loggerName else logging.getLogger()

    def getLogger(self):
        return self.logger

    def setLevel(self, level):
        self.logger.setLevel(level)

    def setFormatter(self, format, formatter=None):
        while self.logger.handlers:
            self.logger.handlers.pop()

        self.formatter = formatter if formatter else JSONStdFormatter(format)
        self.logHandler.setFormatter(self.formatter)

        self.addLogHandlers([
            self.logHandler
        ])

    def addLogHandlers(self, handlers):
        for handler in handlers:
            self.logger.addHandler(handler)

    def _getExtras(self, args, kwargs):
        extras = dict()
        for k, v in kwargs.items():
            extras[k] = v

        extras['message'] = ', '.join([str(arg) for arg in list(args)])
        return extras

    def debug(self, *args, **kwargs):
        extras = self._getExtras(args, kwargs)
        self.logger.debug(extras)

    def info(self, *args, **kwargs):
        extras = self._getExtras(args, kwargs)
        self.logger.info(extras)

    def warning(self, *args, **kwargs):
        extras = self._getExtras(args, kwargs)
        self.logger.warning(extras)

    def error(self, *args, **kwargs):
        extras = self._getExtras(args, kwargs)
        self.logger.error(extras)

    def critical(self, *args, **kwargs):
        extras = self._getExtras(args, kwargs)
        self.logger.critical(extras)


json_std_logger = JSONLoggerStdout()
