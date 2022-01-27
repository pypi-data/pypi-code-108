#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : DeepNN.
# @File         : hashtrick
# @Time         : 2020-04-10 16:54
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import hashlib as _hashlib
from sklearn.utils.murmurhash import murmurhash3_32 as _murmurhash3_32

"""Java
import java.nio.charset.StandardCharsets
import com.google.common.hash.Hashing.murmur3_32

def hash(key: String = "key", value: String = "value", bins: Int = 10000): Int = {
    val hashValue: Int = murmur3_32.newHasher.putString(f"{key}:{value}", StandardCharsets.UTF_8).hash.asInt
    Math.abs(hashValue) % bins  
  }
"""


def md5(string: str, encoding=True):
    s = string.encode('utf8') if encoding else string
    return _hashlib.md5(s).hexdigest()


def murmurhash(key="key", value="value", bins=None, str2md5=True):
    """key:value"""
    string = f"{value}:{key}"
    if str2md5:
        string = md5(string)

    _ = abs(_murmurhash3_32(string, positive=True))  # 与java一致
    return _ % bins if bins else _


class ABTest(object):

    def __init__(self, bins=100, ranger=(0, 9)):
        self.bins = bins
        self.ranger = set(range(*ranger))

    def ab(self, value="value", layer_id='0'):
        string = f"{value}:{layer_id}"

        _ = abs(_murmurhash3_32(string, positive=True)) % self.bins  # 与java一致

        return _ in self.ranger


if __name__ == '__main__':
    print(md5("key:value"))
    print(murmurhash(str2md5=False, bins=10000))  # 3788
    print(murmurhash(str2md5=True, bins=10000))  # 1688 5608
