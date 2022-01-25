# -*- coding:utf-8 -*-

"""

提示：在python文件命名的时候，尽量不要让文件名和类名相同，否则在使用该包时，会报错

"""

import time


# 获取时间戳方法
def timestamp():
    # 去掉时间戳后面的小数
    stamp = int(time.time())
    print('当前时间戳是：', stamp)
    return stamp


def single_get_first(unicode1):
    str1 = unicode1.encode('gbk')
    try:
        ord(str1)
        return str1
    except Exception:
        asc = str1[0] * 256 + str1[1] - 65536
        if -20319 <= asc <= -20284:
            return 'A'
        if -20283 <= asc <= -19776:
            return 'B'
        if -19775 <= asc <= -19219:
            return 'C'
        if -19218 <= asc <= -18711:
            return 'D'
        if -18710 <= asc <= -18527:
            return 'E'
        if -18526 <= asc <= -18240:
            return 'F'
        if -18239 <= asc <= -17923:
            return 'G'
        if -17922 <= asc <= -17418:
            return 'H'
        if -17417 <= asc <= -16475:
            return 'J'
        if -16474 <= asc <= -16213:
            return 'K'
        if -16212 <= asc <= -15641:
            return 'L'
        if -15640 <= asc <= -15166:
            return 'M'
        if -15165 <= asc <= -14923:
            return 'N'
        if -14922 <= asc <= -14915:
            return 'O'
        if -14914 <= asc <= -14631:
            return 'P'
        if -14630 <= asc <= -14150:
            return 'Q'
        if -14149 <= asc <= -14091:
            return 'R'
        if -14090 <= asc <= -13319:
            return 'S'
        if -13318 <= asc <= -12839:
            return 'T'
        if -12838 <= asc <= -12557:
            return 'W'
        if -12556 <= asc <= -11848:
            return 'X'
        if -11847 <= asc <= -11056:
            return 'Y'
        if -11055 <= asc <= -10247:
            return 'Z'
        return ''


def getPinyin(string):
    if string is None:
        return None
    if not '\u4e00' <= string <= '\u9fff':
        return None
    lst = list(string)
    charLst = []
    for l in lst:
        charLst.append(single_get_first(l))
    return ''.join(charLst)


# 测试
if __name__ == '__main__':
    print(getPinyin('啊吧从的饿发非给和就看了吗你哦怕去人是他我下有在'))
