#!/usr/bin/env python3.7
# encoding: utf-8
# 日志文件

import os
import time
import logging
from HTest.get_yaml import get_yaml

LOG_DIR = os.path.join(get_yaml().get('BASE_DIR'), "logs")


class Logger(object):
    """
     终端打印不同颜色的日志，在pycharm中如果强行规定了日志的颜色， 这个方法不会起作用， 但是
     对于终端，这个方法是可以打印不同颜色的日志的。
     在这里定义StreamHandler（控制台输出），可以实现单例， 所有的logger()共用一个StreamHandler
     """
    ch = logging.StreamHandler()

    def __init__(self):
        """ Formatter对象设置日志信息最后的规则、结构和内容如下:
            %(name)s      Logger的名字
            %(levelno)s   数字形式的日志级别
            %(levelname)s 文本形式的日志级别
            %(pathname)s  调用日志输出函数的模块的完整路径名，可能没有
            %(filename)s  调用日志输出函数的模块的文件名
            %(module)s    调用日志输出函数的模块名
            %(funcName)s  调用日志输出函数的函数名
            %(lineno)d    调用日志输出函数的语句所在的代码行
            %(created)f   当前时间，用UNIX标准的表示时间的浮点数表示
            %(relativeCreated)d   输出日志信息时的，自Logger创建以来的毫秒数
            %(asctime)s      字符串形式的当前时间。默认格式是 “2021-11-08 16:49:45,896”。逗号后面的是毫秒
            %(thread)d       线程ID。可能没有
            %(threadName)s   线程名。可能没有
            %(process)d      进程ID。可能没有
            %(message)s      用户输出的消息

        """
        self.logname = os.path.join(LOG_DIR, '%s.log' % time.strftime('%Y%m%d%H%M%S'))
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        # 日志输出格式
        self.formatter = logging.Formatter(
            '[%(asctime)s] [%(filename)s|%(funcName)s] [line:%(lineno)d] %(levelname)-8s: %(message)s')

    def __console(self, level, message):
        if not os.path.isdir(LOG_DIR):
            print("Please specify new project first")
        else:
            # 创建一个FileHandler（文件输出），用于写到本地日志文件
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
        self.ch.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(self.ch)


logger = Logger()

if __name__ == '__main__':
    logger.info(123)
    logger.debug(123)
    logger.warning(123)
    logger.error(123)
