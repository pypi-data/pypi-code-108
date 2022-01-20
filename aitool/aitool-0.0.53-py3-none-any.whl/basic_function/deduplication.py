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
from aitool.basic_function.security import encrypt_md5
from typing import Dict, List, Iterator, Any, NoReturn


def deduplicate(items: Iterator[Any]) -> List[Any]:
    """
    在不影响原顺序的情况下去重
    >>> deduplicate([1,2,3,2,1])
    [1, 2, 3]
    """
    cache = set()
    item_ddp = []
    for item in items:
        if item not in cache:
            cache.add(item)
            item_ddp.append(item)
    return item_ddp


class Deduplication:
    def __init__(self, use_md5: bool = True):
        self.use_md5 = use_md5
        self.data = set()

    def add(self, item: Any) -> NoReturn:
        if not isinstance(item, str):
            item = '{}'.format(item)
        if self.use_md5:
            self.data.add(encrypt_md5(item))
        else:
            self.data.add(item)

    def clean(self):
        self.data = set()

    def is_duplication(self, item: Any, update=True) -> bool:
        """
        判断item是否重复出现。默认使用md5压缩内存。
        :param item:
        :param update:
        :return:
        >>> deduplication = Deduplication()
        >>> for data in [1,1,2]:
        ...     deduplication.is_duplication(data)
        False
        True
        False
        """
        if not isinstance(item, str):
            item = '{}'.format(item)
        if self.use_md5:
            item = encrypt_md5(item)
        if item in self.data:
            return True
        else:
            if update:
                self.data.add(item)
        return False


if __name__ == '__main__':
    import doctest

    doctest.testmod()
