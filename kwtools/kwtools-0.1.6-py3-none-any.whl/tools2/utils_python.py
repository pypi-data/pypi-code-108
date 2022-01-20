import sys
import time
import json
import random
import functools
import logging
import traceback
import pandas as pd
import numpy as np
from retry import retry

from kwtools.settings import logger


def retry_func(func):
    "重试执行的装饰器"
    def wrapper(*args, **kwargs):
        # TODO: 可以传入重试次数... (感觉功能和retry库有点雷同, 还是直接用retry吧...)
        i = 1
        while i <= 3:
            try:
                if i != 1:
                    logger.info(f"尝试第 {i} 次重新执行.....")

                # 被封装的函数
                return func(*args, **kwargs)

            except:
                e = traceback.format_exc(limit=10)
                logger.error(e)
            i += 1
    return wrapper


@retry(tries=3, delay=4, backoff=2, max_delay=8) # 第三方库; (但是没有自定义的功能, 比如打印, 或者其他稍复杂的功能)
# @retry_func # 自己写的;
def test_wrong():
    print(111)
    a = 3/0
    print(222)



class UtilsPython():
    def __init__(self):
        pass


    def p(self, **kwargs):
        k = list(kwargs.keys())[0]
        v = list(kwargs.values())[0]
        print(f"<{k}> {type(v)}: {v}")



utils_python = UtilsPython()




if __name__ == "__main__":
    test_wrong()
