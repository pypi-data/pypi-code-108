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


class Test:
    """
    >>> Test.multiply_by_3(Test(5),2)
    5
    """
    def __init__(self, number):
        self._number=number

    _THREE = 3
    def multiply_by_3(self, x):
        return x*self._number

if __name__ == "__main__":
    import doctest
    doctest.testmod()