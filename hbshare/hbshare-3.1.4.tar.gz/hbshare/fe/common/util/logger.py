# -*- coding: utf-8 -*-

import logging


class Logger:
    def __init__(self,
                 clevel=logging.DEBUG,
                 flevel=logging.DEBUG,
                 name='application',
                 path=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',
                                '%Y-%m-%d %H:%M:%S')
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)
        self.logger.addHandler(sh)
        if path is not None:
            fh = logging.FileHandler(path)
            fh.setFormatter(fmt)
            fh.setLevel(flevel)
            self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)


logger = Logger()
