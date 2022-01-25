# -*- coding:utf-8 -*-
'''
----------------------------------------------------------------
__Author__ : Gemini
__Project__ : package_demo
__File__ : main.py
__Time__ : '2022/1/25 10:56 PM'
----------------------------------------------------------------
___code is far away from bugs with the god animal protecting___
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃        ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛


'''
import itertools

case_list = ['用户名', '密码']
value_list = ['正确', '不正确', '特殊符号', '超过最大长度']


def gen_case(item=case_list, value=value_list):
  '''输出笛卡尔用例集合'''
  for i in itertools.product(item, value):
    print('输入'.join(i))


def print_multiple(n):
  '''打印乘法表的函数'''
  for i in range(n):
    for j in range(i + 1):
      print('%d * %d = %2d' % ((j + 1), (i + 1), (j + 1) * (i + 1)), end='   ')
    print(' ')


def print_msg(msg):
  print("{}".format(msg))


if __name__ == '__main__':
  gen_case()
  print_multiple(9)
