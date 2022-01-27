#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/11 2:39 下午
# @Author  : zhengyu.0985
# @FileName: auto_generate.py
# @Software: PyCharm

# 格式化符替代
template1 = "1、hello %s , your website is %s " % ("Jason", "http://www.baidu.com")

# format函数
template2 = "2、hello {0} , your website is {1} ".format("Jason", "http://www.baidu.com")

# 字符串命名格式化符
template3 = "3、hello %(name)s , your website is %(msg)s " % {"name": "Jason", "msg": "http://www.baidu.com"}
template4 = "4、hello %(name)s , your website is %(msg)s " % ({"name": "Jason", "msg": "http://www.baidu.com"})

# format函数
template5 = "5、hello {name} , your website is {msg} ".format(name="Jason", msg="http://www.baidu.com")

# 模版方法替换：使用string中的Template方法；
from string import Template

my_template = Template("hello ${name} , your website is ${msg} ")
result = my_template.substitute(name="Jason", msg="http://www.baidu.com")


if __name__ == "__main__":
    print(template1)
    print(template2)
    print(template3)
    print(template4)
    print(template5)
    print("*******")
    print(type(result))
    print(result)
