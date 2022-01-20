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
from functools import wraps
from time import sleep
import logging


def retry(
        max_retry_time: int = 3,
        interval: float = 0,
        condition: str = 'no_error',
        callback: Any = None,
):
    if max_retry_time < 0:
        max_retry_time = 0
    if interval < 0:
        interval = 0
    if condition not in ['no_error', 'no_empty']:
        condition = 'no_error'

    def retry_func(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            retry_time = 0
            result = callback

            while retry_time <= max_retry_time:
                if retry_time > 0:
                    logging.warning('retry {} time: {}'.format(func.__name__, retry_time))

                catch_exception = False
                result_empty = False
                try:
                    result = func(*args, **kwargs)
                    if not result:
                        result_empty = True
                except Exception as e:
                    logging.warning(e)
                    catch_exception = True
                if condition == 'no_error' and not catch_exception:
                    break
                if condition == 'no_empty' and not result_empty:
                    break

                sleep(interval)
                retry_time += 1

            return result
        return decorator
    return retry_func


if __name__ == '__main__':
    from random import randint
    @retry(max_retry_time=5)
    def x():
        t = randint(0, 10)
        if t > 2:
            raise ValueError
        return t


    @retry(max_retry_time=5, interval=0.1, condition='no_empty')
    def y():
        t = randint(0, 10)
        if t > 2:
            return
        return t


    print('x', x())
    print('y', y())
