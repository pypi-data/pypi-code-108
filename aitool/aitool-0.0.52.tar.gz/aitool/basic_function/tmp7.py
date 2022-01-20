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
from multiprocessing import Process, Pool, Manager, freeze_support
from time import sleep
from random import random
from collections.abc import Iterable
from os import cpu_count
import functools

def multiprocess_with_queue_old():
    print('xxxxxxxxx')
    queue = Manager().Queue()  # manager是Sync方案，如果直接用Queue()无法与apply_async搭配
    pool = Pool(processes=3)
    for i in range(5):
        print('xddddd', i)
        print(_do_something_with_queue)
        pool.apply_async(_do_something_with_queue, args=(i, queue,))
    pool.close()  # 关闭进程池，表示不能在往进程池中添加进程
    while True:
        sleep(0.1)
        while not queue.empty():
            x = queue.get(False)
            print('get x', x)
            yield x


        # TODO
        # 怎么更好地判断是否所有进程都运行完了
        # 有风险，只能判断在池子里的几个进程
        pool_finished = True
        for app in pool._pool:
            if app.exitcode != 0:
                pool_finished = False
                break
        if pool_finished:
            print('pool finished')
            break
    pool.join()  # 等待进程池中的所有进程执行完毕，必须在close()之后调用


def _do_something_with_queue(x, q):
    for i in range(3):
        print('in {}'.format(i))
        q.put(x)
        print('put {}'.format(i))
        sleep(random())


if __name__ == '__main__':
    # TODO 没确定这个是否有价值
    for x in multiprocess_with_queue_old():
        print('#####')
        print(x)
