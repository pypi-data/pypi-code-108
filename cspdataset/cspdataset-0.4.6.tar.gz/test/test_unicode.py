#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/13 17:08
# @Author  : xgy
# @Site    : 
# @File    : test_unicode.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import html

# s = '&#30417;&#25252;&#34966;&#31456;(&#32418;only)'
s = "测试"
print(html.unescape(s))

# s.decode("unicode_escape").encode('utf-8')

# if __name__ == '__main__':
#     print("start")
