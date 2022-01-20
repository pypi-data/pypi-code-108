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
import re
from typing import Dict, Union, List, Any, NoReturn


def split_dict(data: Dict, keys: List['str']) -> (Dict, Dict):
    # 依据keys筛选出data里key在keys里的数据
    selected_dict = {}
    abandon_dict = {}
    for k, v in data.items():
        if k in keys:
            selected_dict[k] = v
        else:
            abandon_dict[k] = v
    return selected_dict, abandon_dict


def split_char(chars, text):
    chars = re.compile(r'[ ' + chars + r']')
    return re.split(chars, text)


class ReplaceChar:
    # 将text中的old字符（可以有多个）替换为new字符（只能有一个）
    # 实验发现用replace_build_in速度最快
    re_pattern = {}
    char_set = {}

    @classmethod
    def replace_build_in(cls, text: str, old: str, new: str) -> str:
        for char in old:
            text = text.replace(char, new)
        return text

    @classmethod
    def replace_re(cls, text: str, old: str, new: str) -> str:
        if old not in cls.re_pattern:
            cls.re_pattern[old] = re.compile(r'[ ' + old + r']')
        pattern = cls.re_pattern[old]
        return re.sub(pattern, new, text)

    @classmethod
    def replace_generate(cls, text, old, new) -> str:
        if old not in cls.char_set:
            cls.char_set[old] = set(old)
        old_chars = cls.char_set[old]
        result = ''
        for char in text:
            if char not in old_chars:
                result += char
            else:
                result += new
        return result

    @classmethod
    def evaluate(cls, times=10000000):
        """
        >>> ReplaceChar.evaluate()
        replace_build_in 8.00849175453186
        replace_re 23.040991067886353
        replace_generate 13.342495203018188
        """
        import time
        test_case = 'af we，q。gq w'
        b = time.time()
        for i in range(times):
            ReplaceChar.replace_build_in(test_case, ' ，。', '_')
        print('replace_build_in', time.time() - b)
        b = time.time()
        for i in range(times):
            ReplaceChar.replace_re(test_case, ' ，。', '_')
        print('replace_re', time.time() - b)
        b = time.time()
        for i in range(times):
            ReplaceChar.replace_generate(test_case, ' ，。', '_')
        print('replace_generate', time.time() - b)


replace_char = ReplaceChar.replace_build_in


def is_appear(text: str, traits: List[str]) -> bool:
    for trait in traits:
        if trait in text:
            return True
    return False


if __name__ == '__main__':
    ReplaceChar.evaluate()
