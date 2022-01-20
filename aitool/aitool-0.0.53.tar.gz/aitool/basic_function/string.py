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
from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn
from aitool.basic_function.deduplication import deduplicate

def find_all_position(substr: str, text: str) -> List[Tuple[int, int]]:
    """
    找到substr在context里出现的所有位置
    :param substr: 需要查找的文本片段
    :param text: 文本
    :return: substr在context里出现的所有位置
    >>> find_all_position('12', '12312312')
    [(0, 2), (3, 5), (6, 8)]
    """
    return [(i, i + len(substr)) for i in range(len(text)) if text.startswith(substr, i)]


def get_ngram(text: str, ngram: int = 2):
    """
    获取text的所有ngram片段
    :param text: 文本
    :param ngram: 判断的字长
    :return: text的所有ngram片段
    >>> list(get_ngram('abcd'))
    ['ab', 'bc', 'cd']
    """
    for i in range(len(text)-ngram+1):
        yield text[i: i+ngram]


def token_hit(text: str, tokens: Iterator[str]) -> List[str]:
    """
    获取text中包含的token的列表
    :param text: 待处理的文本
    :param tokens: 字符串的列表
    :return: 命中的字符串的列表
    >>> token_hit('1234567', ['1', '34', '9'])
    ['1', '34']
    """
    hit_token = []
    tokens = deduplicate(tokens)
    for token in tokens:
        if token in text:
            hit_token.append(token)
    return hit_token


if __name__ == '__main__':
    import doctest

    doctest.testmod()
