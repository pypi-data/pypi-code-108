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
from tqdm import tqdm
from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn


def conditional_probability(
        conditions: List[Iterator],
        events: List[Iterator],
) -> Tuple[Dict, Dict]:
    """
    依据条件集合和事件集合，假设事件和事件相互独立、条件和条件相互独立，计算出条件概率p(事件|条件)
    :param conditions: 条件集合
    :param events: 事件集合
    :return: {条件: {事件: p(事件|条件)}} 和 {条件: {事件: time(事件|条件)}}
    >>> conditional_probability(['ab', 'b'], [[1, 2], [1, 3, 4]])
    ({'a': {1: 0.5, 2: 0.5}, 'b': {1: 0.4, 2: 0.2, 3: 0.2, 4: 0.2}}, {'a': {1: 1, 2: 1}, 'b': {1: 2, 2: 1, 3: 1, 4: 1}})

    """
    assert len(conditions) == len(events)
    t_c2e = {}
    p_c2e = {}
    for cdt, evt in tqdm(zip(conditions, events), 'statistic condition'):
        for c in cdt:
            for e in evt:
                if c not in t_c2e:
                    t_c2e[c] = {}
                if e not in t_c2e[c]:
                    t_c2e[c][e] = 0
                t_c2e[c][e] += 1
    for c, c2e in tqdm(t_c2e.items(), 'statistic probability'):
        p_c2e[c] = {}
        es, ts = zip(*c2e.items())
        sts = sum(ts)
        for e, t in zip(es, ts):
            p_c2e[c][e] = t/sts
    return p_c2e, t_c2e


if __name__ == '__main__':
    import doctest

    doctest.testmod()
