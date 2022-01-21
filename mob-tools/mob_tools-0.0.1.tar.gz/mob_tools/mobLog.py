# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2022/1/20 20:45
# @Author: "John"

from datetime import datetime

from loguru import logger

logger.add('logs-tet.log', format='{message}')


def formatted_mob_msg(msg, level, class_name='', line_num='', track_id=''):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%S")
    return f'[{ts}  {level}] {class_name}:{line_num} {msg}\n {track_id}'


class MobLogger:

    def __init__(self):
        self._msg = ''
        self._level = ''
        self._track_id = ''

    def debug(self, msg):
        self._msg = msg
        self._level = 'DEBUG'
        return self

    def info(self, msg):
        self._msg = msg
        self._level = 'INFO'
        return self

    def warning(self, msg):
        self._msg = msg
        self._level = 'WARNING'
        return self

    def error(self, msg):
        self._msg = msg
        self._level = 'ERROR'
        return self

    def critical(self, msg):
        self._msg = msg
        self._level = 'CRITICAL'
        return self

    def track_id(self, track_id):
        self._track_id = track_id
        return self

    def commit(self):
        logger.log(self._level, formatted_mob_msg(self._msg, self._level, track_id=self._track_id))


if __name__ == '__main__':
    MobLogger().info('info 级别日志测试2').track_id('test_track_id_2').commit()
