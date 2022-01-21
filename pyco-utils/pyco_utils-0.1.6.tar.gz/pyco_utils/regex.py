import re
from utils.exceptions import ApiError


class PattenItem(object):
    def __init__(self, patten="", note="", key=None, zh=""):
        self.patten = patten
        self.note = note
        self.key = key
        self.zh = zh

    def to_dict(self):
        return vars(self)

    def match(self, value: str, silent=True, key=None):
        m = re.match(self.patten, value)
        if not m and not silent:
            k = key or self.key or self.zh or ''
            msg = '[PattenUnmatched] {}'.format(k)
            raise ApiError(msg=msg, errno=40005, note=self.note)
        return m


class PattenMeta(type):
    def __getattribute__(self, item):
        m = super().__getattribute__(item)
        if isinstance(m, PattenItem) and m.key is None:
            m.key = item
        return m


class RegexMap(metaclass=PattenMeta):
    version = PattenItem(
        patten="\d+(?:\.\d+)*",
        note="由数字和小数点组成，eg: 1.2.4",
        zh="版本号",
    )

    field_key = PattenItem(
        patten='^([a-zA-Z_]+)([a-zA-Z0-9_\.-]){2,63}$',
        note="首字符为字母, 长度不超过64，由字母数字组成的字符串（不允许空格, 符号仅支持_-.）",
        zh='索引键',
    )

    var_name = PattenItem(
        patten="^[A-Za-z_][A-Za-z0-9_]*$",
        note="首字符为字母, 仅由字母数字和下划线组成的字符串",
        zh='变量名',
    )

    var_type = PattenItem(
        patten="^<class '([a-zA-Z]+)'>$",
        note='输入值为type(value), eg: "<class \'int\'>"',
        zh='值类型',
    )

    def __getattribute__(self, item):
        m = super().__getattribute__(item)
        if isinstance(m, PattenItem) and m.key is None:
            m.key = item
        return m

    @classmethod
    def to_dict(cls):
        d = {}
        for k, m in vars(cls).items():
            if isinstance(m, PattenItem):
                d[k] = m.to_dict()
        return d
