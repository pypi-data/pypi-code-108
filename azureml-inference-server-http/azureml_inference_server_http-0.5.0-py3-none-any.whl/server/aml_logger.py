import logging
import sys
import os

class AMLLogger:
    def __init__(self):
        #initializing logger
        level = os.getenv("AZUREML_LOG_LEVEL", "INFO")
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        azureml_logger = logging.getLogger("azureml")
        azureml_logger.setLevel(level)
        azureml_logger.addHandler(stream_handler)

        self.logger = logging.getLogger("root")
        self.logger.setLevel(level)
        self.logger.addHandler(stream_handler)
        self.logger.propagate = False

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

