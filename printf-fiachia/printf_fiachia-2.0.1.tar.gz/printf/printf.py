import os

# windows仅支持8种颜色

os.system("")  # print颜色开启，如果关闭则不能在cmd中显示颜色

# 黑色、红色、绿色、黄色、蓝色、紫红、靛蓝、白色
__color__ = {
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "purple-red": "35",
    "cyanine": "36",
    "white": "37",
    "default": "37",
}
# 黑色、红色、绿色、黄色、蓝色、紫红、靛蓝、白色
__background__ = {
    "black": "40;",
    "red": "41;",
    "green": "42;",
    "yellow": "43;",
    "blue": "44;",
    "purple-red": "45;",
    "cyanine": "46;",
    "white": "47;",
    "default": "",
}
# 默认、高亮、下划线、闪烁、反白、不显示
__effect__ = {
    "default": "0",
    "highlight": "1",
    "underline": "4",
    "flash": "5",
    "backwhite": "7",
    "unshow": "8",
}
# 类型：简化设置
__type__ = {
    "error": ["red", "underline", "default"],
    "warning": ["yellow", "default", "default"],
    "success": ["green", "default", "default"],
    "data": ["blue", "default", "default"],
    "system": ["cyanine", "default", "default"],
    "normal": ["default", "default", "default"],
}


class Format:
    def __init__(self,
                 *value,
                 _color="default",
                 _effect="default",
                 _background="default",
                 _type=None,
                 _isprint=True,
                 sep=' ',
                 end='\n',
                 file=None,
                 flush=False
                 ):
        """

        :param value: 要打印的对象，可不输入，在打印函数输入
        :param _color: 打印颜色
        :param _effect: 打印亮度
        :param _background: 打印背景
        :param _type: 打印类型，可使用自定义类
        :param _isprint: 打印控制
        :param sep: 打印间隔
        :param end: 打印结尾
        :param file: 文件
        :param flush: 流
        """
        self.value = value
        self.color = _color
        self.effect = _effect
        self.background = _background
        self.type = _type
        self.isPrint = _isprint
        self.sep = sep
        self.end = end
        self.file = file
        self.flush = flush
        self.error = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if isinstance(value, tuple):
            self.__value = list(value)
        elif isinstance(value, list):
            self.__value = value
        else:
            self.__value = [value]

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if value is None or value in __color__:
            self.__color = value
        else:
            self.error = "不存在对应颜色"

    @property
    def effect(self):
        return self.__effect

    @effect.setter
    def effect(self, value):
        if value is None or value in __effect__:
            self.__effect = value
        else:
            self.error = "不存在对应亮度"

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, value):
        if value is None or value in __background__:
            self.__background = value
        else:
            self.error = "不存在对应背景"

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value is None or value in __type__:
            self.__type = value
        elif isinstance(value, (tuple, list)):
            __vLen = len(value)
            if __vLen == 0:
                self.error = "请检查输入的类型长度"
            self.__type = None
            self.color = value[0] if __vLen >= 1 else "default"
            self.effect = value[1] if __vLen >= 2 else "default"
            self.background = value[2] if __vLen >= 3 else "default"
        elif isinstance(value, dict):
            self.__type = None
            self.color = value.get("color", default="default")
            self.effect = value.get("effect", default="default")
            self.background = value.get("background", default="default")
        else:
            self.error = "不存在对应背景"

    def reset(self):
        self.color = "default"
        self.effect = "default"
        self.background = "default"
        self.type = None
        self.isPrint = True

    @property
    def isPrint(self):
        return self.__isPrint

    @isPrint.setter
    def isPrint(self, value):
        if isinstance(value, bool):
            self.__isPrint = value
        else:
            self.error = "<isprint>需要<bool>类型的参数"

    def __str__(self):
        if self.type is not None:
            __color = self.type[0]
            __effect = self.type[1]
            __background = self.type[2]
        else:
            __color = self.color
            __effect = self.effect
            __background = self.background
        __print_temp = "\033[%s;%s%sm" % (__effect__[__effect], __background__[__background], __color__[__color])
        if self.value:
            for __value_i in self.value:
                __print_temp += "%s%s" % (__value_i, self.sep)
            __print_temp = __print_temp[:-len(self.sep)]
        __print_temp += "\033[0m%s" % self.end
        return __print_temp

    def __repr__(self):
        return self.__str__()

    def print(self, *value):
        if self.type is not None:
            __color = self.type[0]
            __effect = self.type[1]
            __background = self.type[2]
        else:
            __color = self.color
            __effect = self.effect
            __background = self.background
        print("\033[%s;%s%sm" % (__effect__[__effect], __background__[__background], __color__[__color]),
              sep="", end="", file=self.file, flush=self.flush)
        if value:
            print(*value, sep=self.sep, end="\033[0m%s" % self.end, file=self.file, flush=self.flush)
        else:
            print(*self.value, sep=self.sep, end="\033[0m%s" % self.end, file=self.file, flush=self.flush)

    def __fill(self, __width, __fillchar=" ", __type="L", __parameter=0.35):
        if len(__fillchar) != 1:
            raise OverflowError("填充字符长度只能为1")
        if self.value:
            __value_temp = []
            for __value_i in self.value:
                __value_temp.append(str_just(str(__value_i), __width, __fillchar, _type=__type, _parameter=__parameter))
            return Format(
                *__value_temp,
                _color=self.color,
                _effect=self.effect,
                _background=self.background,
                _type=self.type,
                _isprint=self.isPrint,
                sep=self.sep,
                end=self.end,
                file=self.file,
                flush=self.flush
            )
        return self

    def ljust(self, __width, __fillchar=" ", __parameter=0.35):
        return self.__fill(__width, __fillchar, __type="L", __parameter=__parameter)

    def rjust(self, __width, __fillchar=" ", __parameter=0.35):
        return self.__fill(__width, __fillchar, __type="R", __parameter=__parameter)

    def center(self, __width, __fillchar=" ", __parameter=0.35):
        return self.__fill(__width, __fillchar, __type="C", __parameter=__parameter)


def printf(
        *value,
        _color="default",
        _effect="default",
        _background="default",
        _type=None,
        _isprint=True,
        sep=' ',
        end='\n',
        file=None,
        flush=False
):
    if _type is not None:
        __color = _type[0]
        __effect = _type[1]
        __background = _type[2]
    else:
        __color = _color
        __effect = _effect
        __background = _background
    print("\033[%s;%s%sm" % (__effect__[__effect], __background__[__background], __color__[__color]),
          sep="", end="", file=file, flush=flush)
    print(*value, sep=sep, end="\033[0m%s" % end, file=file, flush=flush)


def str_just(_string, _length, _fillchar=" ", _type="L", _parameter=0.60):
    """
    中英文混合字符串对齐函数
    str_just(_string, _length[, _type]) -> str


    :param _string:[str]需要对齐的字符串
    :param _length:[int]对齐长度
    :param _fillchar:[str]填充字符
    :param _type:[str]对齐方式（'L'：默认，左对齐；'R'：右对齐；'C'或其他：居中对齐）
    :param _parameter:[float] 长度调节参数
    :return:[str]输出_string的对齐结果
    """
    _str_len = len(_string)  # 原始字符串长度（汉字算1个长度）
    num = 0
    for _char in _string:  # 判断字符串内汉字的数量，有一个汉字增加一个长度
        # CJK
        if u'\u2E80' <= _char <= u'\uFE4F':
            num += 1
    _str_len += num * _parameter
    _space = round(_length - _str_len)  # 计算需要填充的空格数
    if _type == 'L':  # 根据对齐方式分配空格
        _left = 0
        _right = _space
    elif _type == 'R':
        _left = _space
        _right = 0
    else:
        _left = _space // 2
        _right = _space - _left
    return "%s" % _fillchar * _left + _string + "%s" % _fillchar * _right


if __name__ == '__main__':
    a = Format("eee", _color="red")
    a.print()
    pass
