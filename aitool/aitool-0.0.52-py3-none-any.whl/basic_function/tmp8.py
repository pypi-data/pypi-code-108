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
from random import random
from time import sleep
from aitool import pool_starmap, multi_map, exe_time
import functools
from collections.abc import Iterable
from os import cpu_count
from random import random
from time import sleep, time
from typing import Iterator, Callable, NoReturn

import multiprocess as mp


def pool_map(
        func: Callable,
        conditions: Iterable,
        processes: int = cpu_count(),
        initializer=None,
        initargs=(),
        maxtasksperchild=None,
):
    # 基于pool.map实现
    with mp.Pool(
            processes=processes,
            initializer=initializer,
            initargs=initargs,
            maxtasksperchild=maxtasksperchild,
    ) as p:
        for result in p.imap(func, conditions):
            yield result

SLEEP_TIME = [random() for _ in range(20)]


def toy(x):
    sleep(x)
    return x


def do_something_in_parent_process(data):
    print(data)


@exe_time(print_time=True)
def test_sequence():
    data = [toy(time) for time in SLEEP_TIME]
    do_something_in_parent_process(data)


@exe_time(print_time=True)
def test_pool_map():
    data = [result for result in pool_map(toy, SLEEP_TIME)]
    do_something_in_parent_process(data)


@exe_time(print_time=True)
def test_pool_starmap():
    data = [result for result in pool_starmap(toy, [[_] for _ in SLEEP_TIME])]
    do_something_in_parent_process(data)


@exe_time(print_time=True)
def test_multi_map():
    data = [result for result in multi_map(toy, SLEEP_TIME)]
    do_something_in_parent_process(data)


print(sum(SLEEP_TIME))
print(SLEEP_TIME)
test_pool_map()
test_pool_starmap()
test_multi_map()
test_sequence()
