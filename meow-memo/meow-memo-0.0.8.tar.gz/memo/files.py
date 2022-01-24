from os import path
import time
from .ioutil import savedDict
from . import myhash
import random
from .paths import pth
__all__ = ["datas", "times"]

datas = savedDict.open(path.join(pth, "datas.json"))
times = savedDict.open(path.join(pth, "timestamp.json"))


def update_data(key, value):
    datas[key] = value
    times[key] = time.time()

