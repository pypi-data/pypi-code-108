import logging
import logging.config
import os

config = {
        "version": 1,
        "formatters": {
            "simple": {"format": "[%(name)s] %(message)s"},
            "complex": {"format": "[%(asctime)s]/[%(name)s]/[%(filename)s:%(lineno)d]/[%(levelname)s]/[%(message)s]"}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG"},
            "file": {
                "class": "logging.FileHandler",
                "filename": "meta.log",
                "formatter": "complex",
                "level": "INFO"}},
            "root": {"handlers": ["console", "file"], "level": "WARNING"},
            "loggers": {
                "ailever": {"level": "INFO"},
                "analysis": {"level": "INFO"},
                "forecast": {"level": "INFO"},
                "database": {"level": "INFO"},
                "dataset": {"level": "INFO"},
                "investment": {"level": "INFO"},
                "dev": {"level": "INFO"},
                "information": {"level": "INFO"},
                },}



class Logger:
    def __init__(self, config=config):
        r"""
        from ..logging_system import logger
        logger['analysis'].info('It's analysis package.')
        logger['investment'].info('It's investment package.')
        """
        logging.config.dictConfig(config)
    
    def __getitem__(self, package):
        package_logging_object = logging.getLogger(package)
        return package_logging_object
        

logger = Logger()
