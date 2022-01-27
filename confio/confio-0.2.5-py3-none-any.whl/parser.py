from enum import Enum
from logging import getLogger

logger = getLogger('confio')


class ConfTypes(Enum):
    """
    配置项的类型
    """

    NONE = ''
    """
    无类型
    """

    EXPR = 'expr'
    """
    表达式
    """

    PATH = 'path'
    """
    路径
    """

    SIZE = 'size'
    """
    文件大小
    """

    TIME = 'time'
    """
    时间值
    """


SIZE = {
    'b': 1,
    'k': 1024,
    'm': 1024 ** 2,
    'g': 1024 ** 3,
    't': 1024 ** 4,
    'p': 1024 ** 5
}

TIME = {
    's': 1,
    'm': 60,
    'h': 60 ** 2,
    'D': 60 ** 2 * 24,
    'M': 60 ** 2 * 24 * 30,
    'Y': 60 ** 2 * 24 * 365,
}


class ValueParser:
    PATH_ROOT = None

    def __init__(self, path_root: str = None):
        self.path_root = path_root or self.PATH_ROOT

    def parse_path(self, value):
        import os
        if not os.path.isabs(value):
            if self.path_root is None:
                raise Exception(
                    'The path root must be specified via `ValueParser.PATH_ROOT=` or `ValueParser(path_root=)`'
                )
            value = os.path.join(self.path_root, value)
        return os.path.abspath(value)

    @classmethod
    def parse_expr(cls, value):
        try:
            return eval(value)
        except Exception as e:
            logger.warning('Cannot evaluate expression "%s": %s' % (value, repr(e)))
            return value

    @classmethod
    def parse_size(cls, value):
        try:
            temp = []
            for ch in value:
                if not ch.isalpha():
                    temp.append(ch)
                    continue
                temp.append('*%s+' % SIZE[ch.lower()])
            # 最后的右边可能存在一个多余的 + 符号
            expr = ''.join(temp).rstrip('+')
            return eval(expr)
        except Exception as e:
            logger.warning('Cannot evaluate size "%s": %s' % (value, repr(e)))
            return int(value)

    @classmethod
    def parse_time(cls, value):
        try:
            temp = []
            for ch in value:
                if not ch.isalpha():
                    temp.append(ch)
                    continue
                temp.append('*%s+' % TIME[ch])
            # 最后的右边可能存在一个多余的 + 符号
            expr = ''.join(temp).rstrip('+')
            return eval(expr)
        except Exception as e:
            logger.warning('Cannot evaluate time "%s": %s' % (value, repr(e)))
            return int(value)
