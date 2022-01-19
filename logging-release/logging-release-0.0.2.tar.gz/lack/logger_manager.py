from .logger import *


class LoggerManager:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    CRITICAL = logging.CRITICAL
    EXCEPTION = logging.ERROR

    main_logger_name = "dynamo"
    main_logger = Logger("dynamo")
    temp_timer_logger = Logger("lack-temp-timer-logger")

    @staticmethod
    def set_main_logger_name(name: str):
        LoggerManager.main_logger = Logger(name)
        LoggerManager.main_logger_name = name

    @staticmethod
    def get_main_logger():
        return LoggerManager.main_logger

    @staticmethod
    def gen_logger(namespace: str):
        return Logger(namespace)

    @staticmethod
    def get_temp_timer_logger():
        return LoggerManager.temp_timer_logger

    @staticmethod
    def progress_logger(generator, logger=None, progress_name="", indent_level=1):
        if logger is None:
            logger = LoggerManager.get_temp_timer_logger()
        iterator = iter(generator)
        logger.log_time()
        i = 0
        prev_progress_percent = 0
        while i < len(generator):
            i += 1
            new_progress_percent = i / len(generator) * 100
            # report every `interval` percent
            if new_progress_percent - prev_progress_percent > 1 or new_progress_percent >= 100:
                logger.report_progress(
                    count=i, total=len(generator), progress_name=progress_name, indent_level=indent_level
                )
                prev_progress_percent = new_progress_percent
            yield next(iterator)
        logger.finish_progress(progress_name=progress_name, indent_level=indent_level)
