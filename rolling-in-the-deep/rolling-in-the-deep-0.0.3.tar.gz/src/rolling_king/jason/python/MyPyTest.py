#!/usr/bin/python
# -*- coding: UTF-8 -*-
import math
import cmath
from collections.abc import Iterable
from collections.abc import Iterator
import argparse

if True:
    print("真")
else:
    print("假")
strVar = input("Please input a number:")
print("strVar is:"+strVar)
print(type(strVar))
num = int(strVar)
print(type(num))
print(num)
# chr(参数是一个ASCII码)，就是将ASCII转为char
print("ASCII码转字符："+chr(49))
print("字符转ASCII码：", ord("A"))

print(len('ABC'))  # 3
strEn = 'ABC'.encode('ascii')
print(strEn)  # string英文转ascii编码的byte数组
print(len(strEn))  # 3
print(len('中文'))  # 2
strCn = '中文'.encode('utf-8')
print(strCn)  # string中文转utf-8编码的byte数组
print(len(strCn))  # 6

print("bytes转str：", b'ABC'.decode('ascii'))
print("bytes转str：", b'\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8'))

# 当Python解释器读取源代码时，为了让它按UTF-8编码读取，我们通常在文件开头写上这两行：
# !/usr/bin/env python3  # 告诉Linux/OS X系统，这是一个Python可执行程序，Windows系统会忽略这个注释；
# -*- coding: utf-8 -*-  # 告诉Python解释器，按照UTF-8编码读取源代码，否则，你在源代码中写的中文输出可能会有乱码。


counter = 100  # 赋值整型变量
miles = 1000.0  # 浮点型
name = "John"  # 字符串
print(counter, miles, name)  # ,代表不换行

counter1, miles1, name1 = 100, 1000.0, "Jason"  # 为多个对象指定多个变量
print(counter1, miles1, name1)

# 标准数据类型:Numbers（数字）、String（字符串）、List（列表）、Tuple（元组）、Dictionary（字典）
var1 = 10
print(var1)
# ----- del用于删除对象的引用
del var1
# print(var1) #del之后此行会报错：NameError: name 'var1' is not defined
var1 = 20
print(var1)


s = "abcdef"
print(s[0:2])  # 包括起始，但不包括结尾。与java的substr函数一致。
print(s[-6:-4])  # 结果均是ab

# 加号（+）是字符串连接运算符，星号（*）是重复操作。
strVal = "Hello World"
print(strVal)           # 输出完整字符串
print(strVal[0])        # 输出字符串中的第一个字符
print(strVal[2:5])      # 输出字符串中第三个至第六个之间的字符串
print(strVal[2:])       # 输出从第三个字符开始的字符串
print(strVal * 2)       # 输出字符串两次
print(strVal + "TEST")  # 输出连接的字符串

# 列表
list = ['runoob', 786, 2.23, 'john', 70.2]
tinylist = [123, 'john']
print(list)  # 输出完整列表
print(list[0])  # 输出列表的第一个元素
print(list[1:3])  # 输出第二个至第三个元素
print(list[2:])  # 输出从第三个开始至列表末尾的所有元素
print(tinylist * 2)  # 输出列表两次
print(list + tinylist)  # 打印组合的列表

list.append('Google')   ## 使用 append() 添加元素
list.append('Runoob')
print(list)

del(list[-2])
print(list)

# 元祖（元组不能二次赋值，相当于只读列表）: Tuple是有序但元素指向不可变。
tuple = ('runoob', 786, 2.23, 'john', 70.2)
tinytuple = (123, 'john')
print(tuple)               # 输出完整元组
print(tuple[0])            # 输出元组的第一个元素
print(tuple[1:3])          # 输出第二个至第四个（不包含）的元素
print(tuple[2:])           # 输出从第三个开始至列表末尾的所有元素
print(tinytuple * 2)       # 输出元组两次
print(tuple + tinytuple)   # 打印组合的元组

#tuple[2] = 1000    # 元组中是非法应用，此行会报错：TypeError: 'tuple' object does not support item assignment
list[2] = 1000     # 列表中是合法应用

tup1 = ()  # 创建空元组
tup1 = (50,)  # 元组中只包含一个元素时，需要在元素后面添加逗号

# 元组中的元素值是不允许修改的，但我们可以对元组进行连接组合.
tup1 = (12, 34.56)
tup2 = ('abc', 'xyz')
tup3 = tup1 + tup2
print("tup3=", tup3)

# 元组中的元素值是不允许删除的，但我们可以使用del语句来删除整个元组
del tup3
# print("After deleting tup3:", tup3)  # NameError: name 'tup3' is not defined


# 字典（列表是有序的对象集合，字典是无序的对象集合）
dict = {}
dict['one'] = "This is one"
dict[2] = "This is two"

tinydict = {'name': 'runoob', 'code':6734, 'dept': 'sales'}

print(dict['one'])          # 输出键为'one' 的值
print(dict[2])              # 输出键为 2 的值
print(tinydict)             # 输出完整的字典
print(tinydict.keys())      # 输出所有键
print(tinydict.values())    # 输出所有值

dict = {'Name': 'Zara', 'Age': 7, 'Class': 'First'}
dict['Age'] = 8  # 更新
dict['School'] = "RUNOOB"  # 添加
del dict['Name']  # 删除键是'Name'的条目
dict.clear()      # 清空字典所有条目
del dict          # 删除字典

# 键必须不可变，所以可以用数字，字符串或元组充当，所以用列表就不行
# dict = {['Name']: 'Zara', 'Age': 7}  # TypeError: unhashable type: 'list'


# 集合Set（Set是无序的、元素唯一不可重复的对象集合)
s = set([1, 2, 3])
print("Set集合：", s)

s = set([1, 1, 2, 2, 3, 3])  # 重复元素在set中自动被过滤
print(s)
s.add(5)
print(s)
s.remove(1)
print(s)

# Set可以看成数学意义上的无序和无重复元素的集合，因此，两个set可以做数学意义上的交集、并集等操作
s1 = set([2, 5, 6, 8])
print("交集：", s & s1)
print("并集：", s | s1)

# if 条件语句
num = 9
if num >= 0 and num <= 10:  # 判断值是否在0~10之间
    print('hello')
# 输出结果: hello

num = 10
if num < 0 or num > 10:  # 判断值是否在小于0或大于10
    print('hello')
else:
    print('undefine')
# 输出结果: undefine

num = 8
# 判断值是否在0~5或者10~15之间
if (num >= 0 and num <= 5) or (10 <= num <= 15):
    print('hello')
elif num < 0:
    print("负数")
else:
    print('undefine')
# 输出结果: undefine


# while 循环
count = 0
while count < 9:
    print('The count is:', count)
    count = count + 1

print("Good bye!")

# while..eles..
# 在 python 中，while … else 在循环条件为 false 时执行 else 语句块：
count = 0
while count < 5:
    print(count, "is less than 5")
    count = count + 1
print("Count is ", count, " now.")

# for 循环1
for letter in 'Python':  # 第一个实例
    print('当前字母 :', letter)

fruits = ['banana', 'apple', 'mango']
for fruit in fruits:  # 第二个实例
    print('当前水果 :', fruit)

print("Good bye!")

# for 循环2:通过索引
fruits = ['banana', 'apple',  'mango']
for index in range(len(fruits)):
    print("Current is ", fruits[index])

for index in range(0, len(fruits)):
    print("Current is ", fruits[index])

print("Good Bye")

# for..else.. 循环 (else 中的语句会在循环正常执行完的情况下执行, 也就意味着不是通过 break 跳出而中断的)
fruits = ['banana', 'apple',  'mango']
for index in range(len(fruits)):
    if index == 3:
        break
    print("index=", index, "'s fruit is ", fruits[index])
else:
    print("Current index = ", index)

# 凡是可作用于for循环的对象都是Iterable类型；
print("是否可迭代：", isinstance('abc', Iterable))  # str是否可迭代 True
print("是否可迭代：", isinstance([1,2,3], Iterable))  # list是否可迭代 True
print("是否可迭代：", isinstance(123, Iterable))  # 整数是否可迭代 False

for i, value in enumerate(['A', 'B', 'C']):
    print(i, value)
# 0 A
# 1 B
# 2 C


# 列表生成式
print("列表生成式")
print([x * x for x in range(1, 11)])
print([x * x for x in range(1, 11) if x % 2 == 0])  # 跟在for后面的if是一个筛选条件，不能带else。
print([x if x % 2 == 0 else -x for x in range(1, 11)])  # 在for前面的部分是一个表达式，必须要算出一个值。
print([m + n for m in 'ABC' for n in 'XYZ'])

# Python中，这种一边循环一边计算的机制，称为生成器：generator
# 第一种方法很简单，只要把一个列表生成式的[]改成()，就创建了一个generator：
g = (x * x for x in range(1, 11))
print(g)
print("使用next函数打印generator", next(g))
for i in g:
    print("使用for循环打印generator：", i)

# 第二种（生成器函数）：一个函数定义中包含yield关键字，那么这个函数就不再是一个普通函数，而是一个generator：
# 在每次调用next()的时候执行，遇到yield语句返回，再次执行时从上次返回的yield语句处继续执行。
# 定义一个generator，依次返回数字1，3，5：
def odd():
    print('step 1')
    yield 1
    print('step 2')
    yield(3)
    print('step 3')
    yield(5)
    return "Done"


gen_func = odd()  # generator函数的“调用”实际返回一个generator对象：
# print(next(gen_func))
# print("-------")
# print(next(gen_func))
# print("-------")
# print(next(gen_func))
# print("-------")
# print(next(gen_func))

# 但是用for循环调用generator时，发现拿不到generator的return语句的返回值。
for n in gen_func:
    print(n)
    print("-------")
print("for循环打印generator完成")

# 如果想要拿到返回值，必须捕获StopIteration错误，返回值包含在StopIteration的value中：
while True:
    try:
        x = next(gen_func)
        print("g: ", x)
    except StopIteration as e:
        print("Generator return value: ", e.value)
        break


# 迭代器：可以被next()函数调用并不断返回下一个值的对象称为迭代器：Iterator。
print(isinstance((x for x in range(10)), Iterator))  # True, generator生成器是迭代器
print(isinstance([], Iterator))  # False
# 生成器都是Iterator对象，但list、dict、str虽然是Iterable，却不是Iterator。
# 这是因为Python的Iterator对象表示的是一个数据流，把这个数据流看做是一个有序序列，
# 但我们却不能提前知道序列的长度，只能不断通过next()函数实现按需计算下一个数据，
# 所以Iterator的计算是惰性的，只有在需要返回下一个数据时它才会计算。
# Iterator甚至可以表示一个无限大的数据流

# 把list、dict、str等Iterable变成Iterator可以使用iter()函数：
print(isinstance(iter([]), Iterator))  # True
print(isinstance(iter("abc"), Iterator))  # True


# pass语句：不做任何事情，一般用做占位语句
for letter in 'Python':
    if letter == 'h':
        pass
        print('这是 pass 块')
    print('当前字母 :', letter)

print("Good bye!")


# Python Number(数字)
# 数据类型是不允许改变的,这就意味着如果改变 Number 数据类型的值，将重新分配内存空间。
var = 0
var1 = 1
var2 = 10
# 使用del语句删除一些 Number 对象引用
del var
del var1, var2

# Python Number 类型转换
# int(x [,base ])         将x转换为一个整数
# long(x [,base ])        将x转换为一个长整数
# float(x )               将x转换到一个浮点数
# complex(real [,imag ])  创建一个复数
# str(x )                 将对象 x 转换为字符串
# repr(x )                将对象 x 转换为表达式字符串
# eval(str )              用来计算在字符串中的有效Python表达式,并返回一个对象
# tuple(s )               将序列 s 转换为一个元组
# list(s )                将序列 s 转换为一个列表
# chr(x )                 将一个整数转换为一个字符
# unichr(x )              将一个整数转换为Unicode字符
# ord(x )                 将一个字符转换为它的整数值
# hex(x )                 将一个整数转换为一个十六进制字符串
# oct(x )                 将一个整数转换为一个八进制字符串
intVal = 0
print(type(intVal))
strVal = str(intVal)
print(type(strVal))
print(hex(15))

# 数学运算
# Python 中数学运算常用的函数基本都在 math 模块、cmath 模块中。
# Python math 模块提供了许多对浮点数的数学运算函数。
# Python cmath 模块包含了一些用于复数运算的函数。
# cmath 模块的函数跟 math 模块函数基本一致，区别是 cmath 模块运算的是复数，math 模块运算的是数学运算。
# 要使用 math 或 cmath 函数必须先导入：import math、import cmath
print(dir(math))
print(dir(cmath))


# 字符串
var1 = 'Hello World!'
var2 = "Python Runoob"
print("var1[0]: ", var1[0])
print("var2[1:5]: ", var2[1:5])

# 成员运算符
if ("ll" in "Hello"):
    print("Hello 包含 ll")
else:
    print("错误")

# 原始字符串
print("反转义")
print(r'\n')  # 反转义

# 字符串格式化使用与 C 中 sprintf 函数一样的语法
print("My name is %s and weight is %d kg!" % ('Zara', 21))

# Python 三引号允许一个字符串跨多行，字符串中可以包含换行符、制表符以及其他特殊字符。
# 三引号让程序员从引号和特殊字符串的泥潭里面解脱出来，当你需要一块HTML或者SQL时，这时当用三引号标记。
errHTML = '''
<HTML><HEAD><TITLE>
Friends CGI Demo</TITLE></HEAD>
<BODY><H3>ERROR</H3>
<B>%s</B><P>
<FORM><INPUT TYPE=button VALUE=Back
ONCLICK="window.history.back()"></FORM>
</BODY></HTML>
'''
print(errHTML)

# Unicode 字符串
# 定义一个 Unicode 字符串
uVar = u'Hello World !'
print(uVar)
# 如果你想加入一个特殊字符，可以使用 Python 的 Unicode-Escape 编码
uVar1 = u'Hello\u0020World !'
print(uVar1)

# Python 日期和时间
import time  # 引入time模块
ticks = time.time()
print("当前时间戳为:", ticks)  # 当前时间戳为: 1603089755.566846

# 时间元祖：很多Python函数用一个元组装起来的9组数字处理时间，也就是struct_time元组。
localtime = time.localtime(time.time())
print("本地时间为：", localtime)  # time.struct_time(tm_year=2020, tm_mon=10, tm_mday=19, tm_hour=14, tm_min=47, tm_sec=46, tm_wday=0, tm_yday=293, tm_isdst=0)
print(time.localtime())  # 等同

asctime = time.asctime(localtime)
print("asc本地时间为：", asctime)   # Mon Oct 19 14:47:46 2020

# 使用 time 模块的 strftime 方法来格式化日期

# 格式化成2016-03-20 11:45:39形式
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# 格式化成Sat Mar 28 22:24:24 2016形式
print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()))

# 将格式字符串转换为时间戳
a = "Sat Mar 28 22:24:24 2016"
print(time.mktime(time.strptime(a, "%a %b %d %H:%M:%S %Y")))

# 处理年历和月历
import calendar
cal = calendar.month(2020, 10)
print("2020年10月的日历：\n", cal)

# Time 模块: 内置函数，既有时间处理的，也有转换时间格式
# time.clock()  # Python 3.8 已移除 clock() 方法，改用下方：
print(time.process_time())

# ArgumentParser
print("ArgumentParser")
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('int_val', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
parser.add_argument("square", help="display a square of a given number", type=int)
args = parser.parse_args()
print("输入的int_val={0}".format(args.int_val))
print("输入的square={0}".format(args.square))
print(args.square**2)
