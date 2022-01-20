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


# TODO
import functools
def get_functions(_func, _iter):
    for condition in _iter:
        yield functools.partial(_func, condition)


if __name__ == '__main__':
    def _do_something(x):
        print('in {}'.format(x))
        for i in range(5):
            print(x)

    data = [1, 2, 3, 4, 5, 6]
    packs = get_functions(_do_something, data)
    for p in packs:
        p()
