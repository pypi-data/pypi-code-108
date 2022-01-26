# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2022/1/26 14:04
# @Author: "John"
import logging
import os
import sys
from datetime import datetime


def log_date_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%S")


def formatted_mob_log_msg(msg, level, class_name='', line_num='', track_id=''):
    formatted_level = '{0:>8}'.format(f'{level}')
    return f'[{log_date_time}  {formatted_level}] {class_name}:{line_num} {msg} {track_id}'


class mobLogger:
    def __init__(self, script_name):
        self._msg = ''
        self._level = ''
        self._track_id = ''
        self._line_num = ''
        self._name = script_name
        self._log = logging.getLogger(script_name)

    def debug(self, msg):
        self._msg = msg
        self._level = 'debug'
        self._log.setLevel('DEBUG')
        return self

    def info(self, msg):
        self._msg = msg
        self._level = 'INFO'
        self._log.setLevel('INFO')
        return self

    def warning(self, msg):
        self._msg = msg
        self._level = 'WARNING'
        self._log.setLevel('WARNING')
        return self

    def error(self, msg):
        self._msg = msg
        self._level = 'ERROR'
        self._log.setLevel('ERROR')
        return self

    def critical(self, msg):
        self._msg = msg
        self._level = 'CRITICAL'
        self._log.setLevel('CRITICAL')
        return self

    def track_id(self, track_id):
        self._track_id = track_id
        return self

    def commit(self):
        formatted_msg = formatted_mob_log_msg(
            self._msg,
            self._level,
            class_name=self._name,
            line_num=self._line_num,
            track_id=self._track_id)

        formatter = logging.Formatter(formatted_msg)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self._log.addHandler(handler)
        self._log.info(formatted_msg)
        pass


if __name__ == '__main__':
    logger = mobLogger(os.path.basename(sys.argv[0]))
    logger.info('info 级别日志测试2').track_id('test_track_id_2').commit()
