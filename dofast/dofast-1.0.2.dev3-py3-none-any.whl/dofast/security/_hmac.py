#!/usr/bin/env python
import base64
import hmac
import os
import time
import codefast as cf


def create_base64_key(bits: int = 42) -> str:
    _bytes = os.urandom(bits)
    return base64.urlsafe_b64encode(_bytes).decode('utf-8')


def generate_token(key: str, expire=3) -> str:
    """
    :param key:  str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key都可以是同一个key)
    :param expire: int(最大有效时间，单位为s)
    :return:  state: str
    refer https://zhuanlan.zhihu.com/p/141623990
    """
    time_str = str(time.time() + expire)
    time_byte = time_str.encode("utf-8")
    sha1_hex = hmac.new(key.encode("utf-8"), time_byte, 'sha1').hexdigest()
    token = time_str + ':' + sha1_hex
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


def certify_token(key: str, token: str) -> bool:
    """
    :param key: str
    :param token: str
    :return:  boolean
    """
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False

    time_str = token_list[0]
    if float(time_str) < time.time():
        return False

    _digest = hmac.new(key.encode("utf-8"), time_str.encode('utf-8'),
                       'sha1').hexdigest()
    _str = (time_str + ':' + _digest).encode('utf-8')
    return token == base64.urlsafe_b64encode(_str).decode('utf-8')
