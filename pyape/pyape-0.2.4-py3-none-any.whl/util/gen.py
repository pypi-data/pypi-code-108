"""
pyape.util.gen
~~~~~~~~~~~~~~~~~~~

生成器
"""

import string
import random
from datetime import datetime

from pyape.util import md5txt
from pyape.util.encrypt import Encrypt


def gen_nonce(k=8, chars=string.ascii_letters + string.digits):
    """ 生成一段加密用的字符串
    字符串可以被用于密码、兑换码等等
    """
    return ''.join(random.choices(chars, k=k))


def gen_password(password, salt):
    """
    计算密码散列后的值
    :param password:
    :param salt:
    :return:
    """
    return md5txt(md5txt(str(password)) + str(salt))


def gen_random_name(value=None, prefix=''):
    """ 提供一个整数和一个前缀，获取一个随机的昵称 """
    if not isinstance(value, int):
        ts = str(datetime.now().timestamp()).split('.')
        value = int(ts[0]) + int(ts[1])
    # 将 value 转成16进制然后倒序
    return prefix + hex(value)[2:][::-1]


# 允许用于 REDIS 的数据类型
DATA_TYPES = ['list', 'string', 'zset', 'hash']
def gen_redis_key_name(r, name, prefix=None, postfix=None, data_type=None, extra=[]):
    """ 生成一个可用的名称，这个名称可能用于配置的键名，或者是排行榜的键名
    
    :param r: regional
    :param name: 名称
    :param prefix: 前缀
    :param postfix: 后缀
    :param date_type: 数据类型。数据类型位于后缀之后
    :param extra: 附加数据
    """
    names = []
    if prefix is not None:
        names.append(str(prefix))
    names.append(str(r))
    names.append(str(name))
    if postfix is not None:
        names.append(str(postfix))
    if data_type in DATA_TYPES:
        names.append(data_type)
    return ':'.join(names + extra)


def gen_sign(**kwargs):
    """ 根据传递来的参数顺序生成校验码
    """
    keys = sorted(kwargs.keys(), key=str.lower)
    k_eq_v = []
    for k in keys:
        value = kwargs[k]
        # 复杂对象、空值、布尔值不参加校验
        if isinstance(value, list) or \
            isinstance(value, dict) or \
            isinstance(value, bool) or \
            value is None:
            continue
        k_eq_v.append(str(k) + '=' + str(value))
    return md5txt('&'.join(k_eq_v))


def gen_secret_key() -> str:
    """ 生成 FLASK 可以使用的 SECRET_KEY
    """
    return Encrypt.fernet_key().decode()