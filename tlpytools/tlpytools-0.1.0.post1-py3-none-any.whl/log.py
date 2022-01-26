import os
import logging
import platform
import datetime
import numpy as np
import pandas as pd
import sqlalchemy as sql
import pyodbc


class logger():
    """set up logger
    """
    def __init__(self) -> None:
        self.log = None

    def init_logger(self, logFile=None, computer='run'):
        # if log file name is None, use source class name
        if logFile == None:
            filename = "{}.log".format(type(self).__name__)
            logFile = filename

        # get computer name
        name = "{}_{}".format(computer, platform.node())

        # try get log handler if it exists
        self.log = logging.getLogger(name)

        # if not, add log handler
        if len(self.log.handlers) == 0:
            # create logger
            self.log = logging.getLogger(name)
            self.log.setLevel(logging.DEBUG)
            # create formatter and add it to the handlers
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            # create file handler
            fh = logging.FileHandler(logFile)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.log.addHandler(fh)
            # create console handler
            ch = logging.StreamHandler()
            # ch.setLevel(logging.ERROR)
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.log.addHandler(ch)

        # log message
        self.log.info('===Logging enabled===')
        self.log.info('Time - {}'.format(datetime.datetime.now()))
        self.log.info("CWD - {d}".format(d=os.getcwd()))
        # print versions
        self.log.info('numpy ' + np.__version__)
        self.log.info('pandas ' + pd.__version__)
        self.log.info('sqlalchemy ' + sql.__version__)
        self.log.info('pyodbc ' + pyodbc.version)
        self.log.info('ipfn ' + "1.4.0")


class analyzer():
    """not implemented: analyze performance of log by analyzing time points
    """
    def __init__(self) -> None:
        self.log = None