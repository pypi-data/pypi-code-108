#!/usr/bin/env python3.7
# encoding: utf-8
#  日志文件
import logging
import time
import os, sys
import setting
sys.path.append(os.path.dirname(__file__))


class Logger(object):
    """
     终端打印不同颜色的日志，在pycharm中如果强行规定了日志的颜色， 这个方法不会起作用， 但是
     对于终端，这个方法是可以打印不同颜色的日志的。
     """
    ch = logging.StreamHandler()  # 在这里定义StreamHandler，可以实现单例， 所有的logger()共用一个StreamHandler

    def __init__(self):
        # 文件的命名
        self.logname = os.path.join(setting.LOG_DIR, '%s.log' % time.strftime('%Y%m%d%H%M%S'))
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        # 日志输出格式
        self.formatter = logging.Formatter(
            '[%(asctime)s] [%(filename)s|%(funcName)s] [line:%(lineno)d] %(levelname)-8s: %(message)s')

    def __console(self, level, message):
        if not os.path.isdir(setting.LOG_DIR):
            print("Please specify new project first")
        else:
            # 创建一个FileHandler，用于写到本地日志文件
            fh = logging.FileHandler(self.logname, encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(self.formatter)
            self.logger.addHandler(fh)

            if level == 'info':
                self.logger.info(message)
            elif level == 'debug':
                self.logger.debug(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'error':
                self.logger.error(message)

            # 避免日志输出重复问题
            self.logger.removeHandler(fh)
            # 关闭打开的文件
            fh.close()

    def debug(self, message):
        self.fontcolor('\033[1;35m%s\033[0m')
        self.__console('debug', message)

    def info(self, message):
        self.fontcolor('\033[1;32m%s\033[0m')
        self.__console('info', message)

    def warning(self, message):
        self.fontcolor('\033[1;33m%s\033[0m')
        self.__console('warning', message)

    def error(self, message):
        self.fontcolor('\033[1;31m%s\033[0m')
        self.__console('error', message)

    def fontcolor(self, color):
        # 终端输出不同颜色
        formatter = logging.Formatter(color % '%(message)s')
        self.ch.setFormatter(formatter)
        self.ch.setLevel(logging.DEBUG)
        self.logger.addHandler(self.ch)


logger = Logger()

if __name__ == '__main__':
    logger.info(123)
    logger.debug(123)
    logger.warning(123)
    logger.error(123)
