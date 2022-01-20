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


class Cache(dict):
    """
    默认使用block模式，仅记录前cache_size个样例
    >>> c = Cache({0: 0}, cache_size=2)
    >>> c[1] = 1
    >>> c[2] = 2
    >>> c[3] = 3
    >>> c
    {0: 0, 1: 1}
    """
    def __init__(self, seq=None, cache_size=100000, method='block', **kwargs):
        """
        :param seq: dict的默认参数
        :param cache_size: cache存储的数量上限
        :param method: cache的控制模式。'block'表示只记录不更新
        :param kwargs: dict的默认参数
        """
        if seq and kwargs:
            super(Cache, self).__init__(seq, **kwargs)
        elif not seq and kwargs:
            super(Cache, self).__init__(**kwargs)
        elif seq and not kwargs:
            super(Cache, self).__init__(seq)
        else:
            super(Cache, self).__init__()
        self.cache_size = cache_size
        self.method = method

    def __setitem__(self, *args, **kwargs):
        if self.method == 'block':
            if self.__len__() < self.cache_size:
                super().__setitem__(*args, **kwargs)


def get_cache(
        cache_size=100000,
) -> dict:
    return Cache(cache_size=cache_size)


def _concat_all(*args, **kwargs) -> str:
    return '{}{}'.format(args, kwargs)


def cache(
        cache_size=100000,
        get_key=_concat_all,
):
    """
    用于修饰某个函数，将自动记录函数的输入输出。
    仅记录前cache_size的输入输出结果，没有淘汰机制。
    :param cache_size: 存储的输入输出对的数量
    :param get_key: 用函数的输入构建key的方法，默认为concat_all
    :return: Any

    在下例中第二次调用不会真正执行repeat函数
    >>> _test_cache()
    In Repeat
    10
    10
    """
    def decorate(func):
        _cache = Cache(cache_size=cache_size)

        def implement(*args, **kwargs):
            key = get_key(*args, **kwargs)
            if key in _cache:
                return _cache[key]
            result = func(*args, **kwargs)
            _cache[key] = result
            return result
        return implement
    return decorate


def _test_cache():
    @cache()
    def repeat(x):
        print('In Repeat')
        return x

    print(repeat(10))
    print(repeat(10))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
