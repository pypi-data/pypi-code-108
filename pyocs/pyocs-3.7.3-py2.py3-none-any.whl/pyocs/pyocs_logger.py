import os
import time
import logging

class PyocsLogger:
    logger = None
    def __init__(self, name, log_file_path=None):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            if log_file_path is None:
                log_file_name = os.getcwd() + "/" + time.strftime('%Y_%m', time.localtime(time.time())) + ".log"
            else:
                log_file_name = log_file_path

            fh = logging.FileHandler(log_file_name, encoding="utf-8")
            ch = logging.StreamHandler()
            formatter = logging.Formatter(fmt='[%(asctime)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def getPyocsLogger(self):
        return self.logger

