from datetime import datetime
import logging
import logging.handlers
from pathlib import Path
import pathlib
from pprint import pformat
import shutil
from typing import Union


class Logger:
    def __init__(
        self,
        logfile_name: str,
        log_dir: Union[Path, str, None]=None,
        level=logging.DEBUG,
        mode="w",
        add_timestamp_to_filename=True,
        is_console_only=False,
        is_null_handler=False,
        is_rolling_handler=False,
        process: str = None,
    ):
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        if is_null_handler:
            logger = logging.getLogger()
            logger.addHandler(logging.NullHandler())
            logger.setLevel(level)
            self.log_file_path = None  # no logfile
            self._logger = logger
            self.process = process if process else ""
            return

        if logfile_name and log_dir and not is_console_only:
            # append timestamp and extension to file
            if logfile_name != "test" and add_timestamp_to_filename:
                logfile_name += "_" + datetime.now().strftime("%Y%m%d_%H%M_%S")

            # append process name if provided
            if process:
                logfile_name += "_" + process

            logfile_name += ".log"
            log_path = pathlib.Path(log_dir) / logfile_name
            self.log_file_path = log_path

            logger = logging.getLogger(logfile_name)  # create logging instance
            logger.setLevel(level)

            if is_rolling_handler:
                handler = logging.handlers.RotatingFileHandler(
                    log_path, maxBytes=5_000_000, backupCount=5, mode=mode
                )
            else:
                handler = logging.FileHandler(log_path, mode=mode)

            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        else:
            logger = logging.getLogger()
            logger.setLevel(level)
            self.log_file_path = None

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self._logger = logger
        self.process = process if process else ""

        # if process is set by client, it will be shown on each log line

    def _add_process_and_data_to_message(self, message, data):
        if self.process:
            message = self.process + " - " + message
        if data:
            message += "\n" + pformat(data, width=200) + "\n"
        return message

    def info(self, message: str, data=None):
        message = self._add_process_and_data_to_message(message, data)
        self._logger.info(message)

    def debug(self, message: str, data=None):
        message = self._add_process_and_data_to_message(message, data)
        self._logger.debug(message)

    def error(self, message: str, data=None):
        message = self._add_process_and_data_to_message(message, data)
        self._logger.error(message)

    def warning(self, message: str, data=None):
        message = self._add_process_and_data_to_message(message, data)
        self._logger.warning(message)

    def exception(self, message: str, data=None):
        message = self._add_process_and_data_to_message(message, data)
        self._logger.exception(message)

    def shut_down(self):
        handlers = self._logger.handlers[:]
        for handler in handlers:
            handler.close()

    def get_log_file_path(self):
        return self.log_file_path

    def set_custom_filter(self, filter_function):
        self._logger.filter = filter_function

    def shut_down_and_append_error_to_filename(self) -> Path:
        """Copies log file to a new file with __ERROR__ appended to the name.
        Returns path to new file."""
        self.shut_down()

        f = self.log_file_path
        if f is None:
            return None
        name, ext = f.name.split(".")
        new_name = name + "__ERROR__." + ext
        new_path = f.parent / new_name

        shutil.move(f, new_path)

        return new_path
