from logging import getLogger, FileHandler, StreamHandler, Formatter, Handler, INFO, WARNING

from os.path import exists
import json
import requests

loggers = {}
log_file_format = \
    "[%(asctime)s][%(levelname)s]|%(module)s.%(funcName)s:%(lineno)d| %(message)s"


def myLogger(name, app_path='.', log_dir='data/logs', log_name='application', config=None):
    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = getLogger(name)
        logger.setLevel(INFO)
        stderr_log_handler = StreamHandler()
        formatter = Formatter(log_file_format, datefmt="%d %b %Y %H:%M:%S")
        log_dir = f'{app_path}/{log_dir}'
        if exists(log_dir):
            log_path = f'{log_dir}/{log_name}.log'
            file_log_handler = FileHandler(log_path)
            file_log_handler.setFormatter(formatter)
            logger.addHandler(file_log_handler)
        stderr_log_handler.setFormatter(formatter)
        logger.addHandler(stderr_log_handler)
        slack_handler = SlackLogHandler(config=config)
        slack_handler.setLevel(WARNING)
        logger.addHandler(slack_handler)
        loggers[name] = logger

        return logger


class SlackLogHandler(Handler):
    EMOJIS = {
        "CRITICAL": ":boom:",
        "ERROR": ":x:",
        "WARNING": ":warning:",
        "NOTSET": ":question:",
    }

    def __init__(self, config=None):
        Handler.__init__(self)
        self.config = config

    def emit(self, record):
        try:
            if self.config and self.config.slack_url:
                json_data = json.dumps({
                    "text": f"{record.asctime} - {record.module} - {record.msg}",
                    "username": f"{record.levelname} - {record.process}",
                    "icon_emoji": self.EMOJIS.get(record.levelname, self.EMOJIS["NOTSET"])
                })
                requests.post(self.config.slack_url, data=json_data.encode(
                    'ascii'), headers={'Content-Type': 'application/json'})
        except Exception as em:
            print("EXCEPTION: " + str(em))
