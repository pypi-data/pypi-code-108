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
import json
from typing import Dict, Union, List, Any, NoReturn, Iterable, Tuple, Generator
import numpy as np
from bs4 import BeautifulSoup


def flatten(data: Union[List[Any], Tuple[Any]], ignore_types: tuple = (str, bytes)) -> Generator:
    """
    flatten list or tuple
    :param data: a list or a tuple
    :param ignore_types: types will not be flatten
    :return: a generator of a flatten list

    >>> [x for x in flatten([[1,2,('abc',4)],'hello'])]
    [1, 2, 'abc', 4, 'hello']
    >>> [x for x in flatten('abc')]
    ['abc']
    """

    if isinstance(data, Iterable) and not isinstance(data, ignore_types):
        for item in data:
            if isinstance(item, Iterable) and not isinstance(item, ignore_types):
                yield from flatten(item)
            else:
                yield item
    else:
        yield data


def html2text(html: str):
    content = BeautifulSoup(html, 'lxml').text
    content = content.replace('\xa0', ' ')
    return content


def content2text(data: Any, debug: bool = True):
    """
    提取以下两种数据格式中的文本部分：
    1、html格式
    2、'[{'info':'text'}, {'info':'text'}]'
    :param data: 待处理的数据格式
    :param debug: debug模式下会打印报错信息
    :return: content中的文本格式
    """
    content = ''
    try:
        for item in eval(data):
            if 'info' in item:
                content += item['info']
    except Exception as e1:
        try:
            content = html2text(data)
        except Exception as e2:
            if debug:
                print(data)
                print(e1, e2)
    return content


def _format_kv_data(data, str_format=True):
    if str_format:
        return '{}'.format(data)
    return data


def _get_kv_pair(
        data,
        pre='',
        only_leaf=True,
        str_format=False,
        do_eval=False,
        key_eval=None,
        key_skip=None,
        separator_key='$k.',
        separator_index='$i.',
):
    # 将复杂json格式
    kv_pair = []

    if key_skip and pre in key_skip:
        return kv_pair

    if do_eval:
        try:
            if key_eval is None or pre in key_eval:
                kv_pair.extend(_get_kv_pair(eval(data), pre=pre, only_leaf=only_leaf, str_format=str_format,
                                            do_eval=do_eval, key_eval=key_eval, key_skip=key_skip,
                                            separator_key=separator_key, separator_index=separator_index))
                return kv_pair
        except (TypeError, SyntaxError, NameError):
            pass
        try:
            if key_eval is None or pre in key_eval:
                kv_pair.extend(_get_kv_pair(json.loads(data), pre=pre, only_leaf=only_leaf, str_format=str_format,
                                            do_eval=do_eval, key_eval=key_eval, key_skip=key_skip,
                                            separator_key=separator_key, separator_index=separator_index))
                return kv_pair
        except (TypeError, SyntaxError, NameError, json.decoder.JSONDecodeError):
            pass

    if isinstance(data, dict):
        if not only_leaf:
            kv_pair.append((pre, _format_kv_data(data, str_format=str_format)))
        for k, v in data.items():
            kv_pair.extend(_get_kv_pair(v, pre=pre + separator_key + str(k), only_leaf=only_leaf, str_format=str_format,
                                        do_eval=do_eval, key_eval=key_eval, key_skip=key_skip,
                                        separator_key=separator_key, separator_index=separator_index))
    elif isinstance(data, (list, tuple, set)):
        if not only_leaf:
            kv_pair.append((pre, _format_kv_data(data, str_format=str_format)))
        for index, d in enumerate(data):
            kv_pair.extend(_get_kv_pair(d, pre=pre + separator_index + str(index), only_leaf=only_leaf,
                                        str_format=str_format, do_eval=do_eval, key_eval=key_eval, key_skip=key_skip,
                                        separator_key=separator_key, separator_index=separator_index))
    else:
        kv_pair.append((pre, _format_kv_data(data, str_format=str_format)))
    return kv_pair


def split_part(text: str, sep: List[str]) -> List[str]:
    """
    依据sep做切分。对sep的匹配是贪心的。
    :param text:
    :param sep:
    :return:

    >>> split_part('1234512345', ['1', '34'])
    ['1', '2', '34', '5', '1', '2', '34', '5']
    """
    sp_text = []
    head = 0
    last_head = 0
    while head < len(text):
        for s in sep:
            if text[head:head + len(s)] == s:
                if head > last_head:
                    sp_text.append(text[last_head:head])
                sp_text.append(text[head:head + len(s)])
                head = head + len(s)
                last_head = head
                break
        head += 1
    if last_head < len(text):
        sp_text.append(text[last_head:])
    return sp_text


def get_pair(
        data,
        only_leaf=True,
        str_format=False,
        do_eval=False,
        key_eval=None,
        key_skip=None,
        separator='.',
        fullname=True,
        show_index=False,
):
    """

    :param data:
    :param only_leaf:
    :param str_format:
    :param do_eval:
    :param key_eval:
    :param key_skip:
    :param separator:
    :param fullname:
    :param show_index:
    :return:

    # 基础用法
    >>> data = {1:2, 3:{4:[5,6]}, 7:'{8,9}'}
    >>> get_pair(data)
    [['1', 2], ['3.4', 5], ['3.4', 6], ['7', '{8,9}']]

    # 修改连接符
    >>> data = {1:2, 3:{4:[5,6]}, 7:'{8,9}'}
    >>> get_pair(data, separator='->')
    [['1', 2], ['3->4', 5], ['3->4', 6], ['7', '{8,9}']]

    # 输出简短的名称
    >>> data = {1:2, 3:{4:[5,6]}, 7:'{8,9}'}
    >>> get_pair(data, fullname=False)
    [['1', 2], ['4', 5], ['4', 6], ['7', '{8,9}']]

    # 对字符串进行解析
    >>> data = {1:2, 3:{4:[5,6]}, 7:'{8,9}'}
    >>> get_pair(data, do_eval=True)
    [['1', 2], ['3.4', 5], ['3.4', 6], ['7', 8], ['7', 9]]

    # 同时输出非叶子的pair对
    >>> data = {1:2, 3:{4:[5,6]}}
    >>> get_pair(data, only_leaf=False)
    [['', {1: 2, 3: {4: [5, 6]}}], ['1', 2], ['3', {4: [5, 6]}], ['3.4', [5, 6]], ['3.4', 5], ['3.4', 6]]
    """
    if not fullname:
        show_index = False
    separator_key = '$$@@key.'
    separator_index = '$$@@ind.'
    kv_pair = _get_kv_pair(
        data,
        pre='',
        only_leaf=only_leaf,
        str_format=str_format,
        do_eval=do_eval,
        key_eval=key_eval,
        key_skip=key_skip,
        separator_key=separator_key,
        separator_index=separator_index)

    pair = []
    for k, v in kv_pair:
        name_part = []
        need = True
        for k_sp in split_part(k, [separator_key, separator_index]):
            if k_sp == separator_index:
                if not show_index:
                    need = False
                continue
            if k_sp == separator_key:
                continue
            if need:
                name_part.append(k_sp)
            else:
                need = True
        if fullname:
            name = separator.join(name_part)
        else:
            name = name_part[-1] if len(name_part) > 0 else ''
        pair.append([name, v])

    return pair


def np2list(data):
    """

    :param data:
    :return:

    >>> data = np.array([[1, 2], [3, 4]])
    >>> print(np2list(data))
    [[1, 2], [3, 4]]
    """
    _type = type(data)
    if _type == np.ndarray:
        if data.ndim >= 1:
            return [np2list(d) for d in data]
    if _type in [np.int0, np.int8, np.int16, np.int32, np.int64]:
        return int(data)
    return data


if __name__ == '__main__':
    import doctest

    doctest.testmod()
