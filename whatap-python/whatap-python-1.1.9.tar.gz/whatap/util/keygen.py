from whatap.util.date_util import DateUtil
import random
try:
    random.seed(DateUtil.nowSystem())
except:
    pass

class KeyGen(object):
    @classmethod
    def next(cls):
        return int(random.random()*0x7fffffff)
