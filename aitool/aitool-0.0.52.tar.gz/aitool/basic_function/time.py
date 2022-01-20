# -*- coding: UTF-8 -*-
# Copyright©2020 xiangyuejia@qq.com All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

"""
from typing import Dict, Union, List, Any, NoReturn
from time import sleep
import time
import sys
import threading


class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()
    method.
    Come from:
    Kill a thread in Python:
    http://mail.python.org/pipermail/python-list/2004-May/260937.html
    """
    def __init__(self, *args, **kwargs) -> NoReturn:
        threading.Thread.__init__(self, *args, **kwargs)
        self.killed = False

    def start(self) -> NoReturn:
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to install our trace.
        threading.Thread.start(self)

    def __run(self) -> NoReturn:
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg) -> NoReturn:
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg) -> NoReturn:
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self) -> NoReturn:
        self.killed = True


def timeout(seconds: float, callback: Any):
    """
    若被装饰的方法在指定的时间内未返回，会提前终止，并返回callback
    :param seconds: 超时时长（秒）
    :param callback: 超时时的返回值
    :return: 
    """
    def timeout_func(func):
        def _new_func(target_func, result, target_func_args, target_func_kwargs):
            result.append(target_func(*target_func_args, **target_func_kwargs))

        def decorate(*args, **kwargs):
            result = []
            new_kwargs = {
                'target_func': func,
                'result': result,
                'target_func_args': args,
                'target_func_kwargs': kwargs
            }
            thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)
            thd.start()
            thd.join(seconds)
            alive = thd.isAlive()
            thd.kill()  # kill the child thread
            if alive:
                try:
                    pass
                finally:
                    return callback
            else:
                if len(result) > 0:
                    return result[0]
                return
        decorate.__name__ = func.__name__
        decorate.__doc__ = func.__doc__
        return decorate
    return timeout_func


def timestamp(style=None):
    _t = time.localtime(time.time())
    if style == 'day':
        describe = '{}_{}_{}'.format(_t.tm_year, _t.tm_mon, _t.tm_mday)
    elif style == 'hour':
        describe = '{}_{}_{}_{}'.format(_t.tm_year, _t.tm_mon, _t.tm_mday, _t.tm_hour)
    elif style == 'min':
        describe = '{}_{}_{}_{}:{}'.format(_t.tm_year, _t.tm_mon, _t.tm_mday, _t.tm_hour, _t.tm_min)
    elif style == 'sec':
        describe = '{}_{}_{}_{}:{}:{}'.format(_t.tm_year, _t.tm_mon, _t.tm_mday, _t.tm_hour, _t.tm_min, _t.tm_sec)
    elif style is None:
        describe = '{}'.format(time.asctime(_t))
        describe = describe.replace('  ', '_')
        describe = describe.replace(' ', '_')
    else:
        raise ValueError('style: {}'.format(style))
    return describe


if __name__ == '__main__':
    @timeout(2.2, None)  # 限时 2 秒超时
    def connect(time):  # 要执行的函数
        sleep(time)  # 函数执行时间，写大于2的值，可测试超时
        print('Finished without timeout.')
        return 'sss'

    x = connect(1.2)
    print(x)
    y = connect(2.5)
    print(y)

    print(timestamp(style='sec'))
