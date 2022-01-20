# -*- coding: UTF-8 -*-
# @Time    : 2021/3/10
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import time


def exe_time(print_time=False, detail=False):
    def wrapper(func):
        def decorate(*args, **kw):
            t0 = time.time()
            if detail:
                print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__))
            back = func(*args, **kw)
            if detail:
                print("@%s, {%s} finish" % (time.strftime("%X", time.localtime()), func.__name__))
            if print_time:
                print("@%.3fs taken for {%s}" % (time.time() - t0, func.__name__))
            return back
        return decorate
    return wrapper


if __name__ == '__main__':
    @exe_time()
    def test1():
        print('i am from england')


    @exe_time(print_time=True)
    def test2():
        print('i am from england')


    @exe_time(detail=True)
    def test3():
        print('i am from england')


    test1()
    test2()
    test3()
