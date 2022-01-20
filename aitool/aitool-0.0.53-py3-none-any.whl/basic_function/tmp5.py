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
from multiprocessing import Process, Pool, Manager, freeze_support, Queue
from time import sleep
from random import random
from collections.abc import Iterable
from os import cpu_count
import functools


def _process(pid, data):
    # TODO
    pic_id = 1
    while True:
        print('In Proc 爬第{}个网站的第{}张图'.format(pid, pic_id))
        pic_id += 1
        sleep(random())


def get_tips():
    process_count = 3
    process_list = []
    for process_id in range(process_count):
        # TODO
        print('In Main 爬第{}个网站'.format(process_id))
        p = Process(target=_process, args=(process_id, []))
        process_list.append(p)
        p.start()
        sleep(2)

    for index, p in enumerate(process_list):
        print('In Main join process {}'.format(index))
        p.join()
    print('In Main  finish join')


def multiprocess(_func, _iterator):
    pool = Pool(processes=4)
    for i in range(10):
        pool.apply_async(_func, (i,))
    pool.close()  # 关闭进程池，表示不能在往进程池中添加进程
    pool.join()  # 等待进程池中的所有进程执行完毕，必须在close()之后调用


def get_functions(_func, /, _iter):
    for condition in _iter:
        if not isinstance(condition, Iterable):
            yield functools.partial(_func, condition)
        elif type(condition) == dict:
            yield functools.partial(_func, **condition)
        elif type(condition) == list:
            yield functools.partial(_func, *condition)
        elif type(condition) == tuple and len(condition) == 2:
            args, keywords = condition
            yield functools.partial(_func, *args, **keywords)
        else:
            raise ValueError('不能识别的参数格式')


def _return_2_queue_old(function):
    def _fun_with_queue(queue, _func=None):
        result = _func()
        print(_fun_with_queue, result)
        queue.put(result)
    return functools.partial(_fun_with_queue, _func=function)


def _return_2_queue_bad(function):
    def _fun_with_queue(queue):
        result = function()
        print(_fun_with_queue, result)
        queue.put(result)
    return _fun_with_queue

# yield functools.partial(_func, condition)


def _return_2_queue(function, queue):
    result = function()
    print(function, result)
    queue.put(result)


def multiprocess_with_queue(functions, processes=cpu_count()):
    print('processes', processes)
    queue = Manager().Queue()  # manager是Sync方案，如果直接用Queue()无法与apply_async搭配
    # queue = Queue()  # manager是Sync方案，如果直接用Queue()无法与apply_async搭配
    pool = Pool(processes=processes)
    for function in functions:
        print('sssss')
        print(function)
        # new_func = _return_2_queue(function)
        # print('ttttt')
        # print(new_func)
        # new_func(queue)
        # p = Process(target=new_func, args=(queue,))
        # p = Process(target=new_func)
        # print(p.daemon)
        # p.start()
        pool.apply_async(_return_2_queue, args=(function, queue,))
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


# TODO
# 多进程多线程的池都建议使用 concurrent.futures 里面那俩,
# 借助很多语言都在流行的 Future 概念, 可以在同步代码里面把异步操作简化.
# 尤其是借助 callback 方式

def test_get_functions():
    def _do_something(x):
        print('in {}'.format(x))
        for i in range(5):
            print(x)

    data = [1, 2, 3, 4, 5, 6]
    packs = get_functions(_do_something, data)
    for p in packs:
        p()


def _do_something(x, y=1):
    print('in {} {}'.format(x, y))
    sleep(random())
    return x

def do_some_1():
    return _do_something(1)

def do_some_2():
    return _do_something(2)

if __name__ == '__main__':
    # TODO 没确定这个是否有价值
    # freeze_support()

    # get_tips()
    # multiprocess(_do_something, [])

    # for x in multiprocess_with_queue(_do_something_with_queue):
    #     pass


    #
    #
    # data = [1, [2, 3], {'x': 4}, {'x': 6, 'y': 7}]
    # packs = list(get_functions(_do_something, data))
    # for p in packs:
    #     p()

    packs = [do_some_1, do_some_2]

    # queue = Manager().Queue()
    # tmps = []
    # for p in packs:
    #     tmps.append(_return_2_queue(p))
    # for t in tmps:
    #     t(queue)
    #
    for x in multiprocess_with_queue(packs):
        print(x)


    # !!!! 多进程只能处理根下的函数
    # AttributeError: Can't pickle local object '_return_2_queue.<locals>._fun_with_queue'
    # 得这中才行
    #
