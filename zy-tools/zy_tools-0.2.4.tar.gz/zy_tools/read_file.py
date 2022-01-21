# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2020/3/27 16:30
# @Author: "John"


def read_big_file(fl, newline="{|}", fl_limit=4096):
    """
        :return iterator
    :param fl:  file name
    :param newline:
    :param fl_limit:
    :return:
    """
    buf = ""
    while True:
        while newline in buf:
            pos = buf.index(newline)
            yield buf[:pos]
            buf = buf[pos + len(newline):]
        chunk = fl.read(fl_limit)

        if not chunk:
            # 说明已经读到了文件结尾
            yield buf
            break
        buf += chunk
