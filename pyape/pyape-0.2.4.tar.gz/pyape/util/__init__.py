__all__ = ['encrypt', 'func']

import hashlib
import base64


def md5txt(txt):
    """
    计算 MD5 字符串散列
    :param txt:
    :return:
    """
    md5obj = hashlib.md5()
    md5obj.update(txt.encode('utf-8'))
    return md5obj.hexdigest()


def md5base64(txt):
    """ md5(base64) 算法
    验证工具： http://www.cmd5.com/hash.aspx
    """
    m = hashlib.md5()
    m.update(txt.encode('utf8'))
    return base64.encodebytes(m.digest())[:-1].decode('utf8')