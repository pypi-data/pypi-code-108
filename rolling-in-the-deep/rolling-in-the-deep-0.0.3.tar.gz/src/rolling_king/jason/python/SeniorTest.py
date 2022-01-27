#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from functools import reduce
import functools

# ################### 闭包 ###################
# 闭包的定义:在函数嵌套的前提下，内部函数使用了外部函数的变量，并且外部函数返回了内部函数，这种程序结构称为闭包。
# 闭包的构成条件：
# 1、在函数嵌套(函数里面再定义函数)的前提下
# 2、内部函数使用了外部函数的变量(还包括外部函数的参数)
# 3、外部函数返回了内部函数

# 定义一个外部函数
def func_out(num1):
    # 定义一个内部函数
    def func_inner(num2):
        # 内部函数使用了外部函数的变量(num1)
        result = num1 + num2
        print("结果是:", result)
    # 外部函数返回了内部函数，这里返回的内部函数就是闭包
    return func_inner

# 创建闭包实例
f = func_out(1)
# 执行闭包
f(2)  # 3
f(3)  # 4

# 若要修改外部函数的变量，则内部函数中应该：
# nonlocal num1  # 告诉解释器，此处使用的是 外部变量a
# 修改外部变量num1
# num1 = 10


# ################### 装饰器 ###################
# 装饰器的定义：就是给已有函数增加额外功能的函数，它本质上就是一个闭包函数。
# 代码运行期间动态增加功能的方式，称之为“装饰器”（Decorator）。
# 装饰器的功能特点:
# 1、不修改已有函数的源代码
# 2、不修改已有函数的调用方式
# 3、给已有函数增加额外的功能

# 添加一个登录验证的功能
def check(fn):
    def inner():
        print("请先登录....")
        fn()
    return inner


def comment():
    print("发表评论")

# 使用装饰器来装饰函数
comment = check(comment)
comment()
'''
执行结果
请先登录....
发表评论
'''

# 装饰器的基本雏形
# def decorator(fn): # fn:目标函数.
#     def inner():
#         '''执行函数之前'''
#         fn() # 执行被装饰的函数
#         '''执行函数之后'''
#     return inner

# 代码说明:
# 闭包函数有且只有一个参数，必须是函数类型，这样定义的函数才是装饰器。
# 写代码要遵循开放封闭原则，它规定已经实现的功能代码不允许被修改，但可以被扩展。


# 装饰器的语法糖写法
# Python给提供了一个装饰函数更加简单的写法，那就是语法糖，语法糖的书写格式是: @装饰器名字，通过语法糖的方式也可以完成对已有函数的装饰
# 使用语法糖方式来装饰函数
@check
def comment():
    print("发表评论")


# @check 等价于 comment = check(comment)
# 装饰器的执行时间是加载模块时立即执行。


# ###### 装饰带有参数的函数 ######
def logging(fn):
    def inner(num1, num2):
        print("--正在努力计算--")
        fn(num1, num2)

    return inner


# 使用装饰器装饰函数
@logging
def sum_num(a, b):
    result = a + b
    print(result)


sum_num(1, 2)
'''
运行结果:
--正在努力计算--
3
'''

# ###### 装饰带有返回值的函数 ######
# 添加输出日志的功能
def logging(fn):
    def inner(num1, num2):
        print("--正在努力计算--")
        result = fn(num1, num2)
        return result
    return inner


# 使用装饰器装饰函数
@logging
def sum_num(a, b):
    result = a + b
    return result


result = sum_num(1, 2)
print(result)
'''
运行结果:
--正在努力计算--
3
'''


# ###### 装饰带有不定长参数的函数 ######
# 添加输出日志的功能
def logging(func):
    def inner(*args, **kwargs):
        print("--正在努力计算--")
        func(*args, **kwargs)

    return inner


# 使用语法糖装饰函数
@logging
def sum_num(*args, **kwargs):
    result = 0
    for value in args:
        result += value

    for value in kwargs.values():
        result += value

    print(result)

sum_num(1, 2, a=10)
'''
运行结果:
--正在努力计算--
13
'''


# ###### 通用装饰器 ######
# 通用装饰器 - 添加输出日志的功能
def logging(func):
    def inner(*args, **kwargs):
        print("--正在努力计算--")
        result = func(*args, **kwargs)
        return result

    return inner


# 使用语法糖装饰函数
@logging
def sum_num(*args, **kwargs):
    result = 0
    for value in args:
        result += value

    for value in kwargs.values():
        result += value

    return result


@logging
def subtraction(a, b):
    result = a - b
    print(result)

result = sum_num(1, 2, a=10)
print(result)

subtraction(4, 2)
'''
运行结果:
--正在努力计算--
13
--正在努力计算--
2
'''

# log方法作为装饰器，返回替代func方法的wrapper方法，利用@functools.wraps表示，以便让wrapper.__name__等同于func.__name__。
def log(func):
    @functools.wraps(func)  #import functools才行
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper

# 针对带参数的decorator：
def log_with_param(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator



# ###### 多个装饰器的使用  ######
# 代码说明:多个装饰器的装饰过程是: 离函数最近的装饰器先装饰，然后外面的装饰器再进行装饰，由内到外的装饰过程。
def make_div(func):
    """对被装饰的函数的返回值 div标签"""
    def inner():
        return "<div>" + func() + "</div>"
    return inner


def make_p(func):
    """对被装饰的函数的返回值 p标签"""
    def inner():
        return "<p>" + func() + "</p>"
    return inner


# 装饰过程: 1 content = make_p(content) 2 content = make_div(content)
# content = make_div(make_p(content))
@make_div
@make_p
def content():
    return "人生苦短"

result = content()

print(result) # <div><p>人生苦短</p></div>



# ################### 带有参数的装饰器 ###################
# 代码说明:装饰器只能接收一个参数，并且还是函数类型。
# 正确写法:在装饰器外面再包裹上一个函数，让最外面的函数接收参数，返回的是装饰器，因为@符号后面必须是装饰器实例。

# 添加输出日志的功能
def logging(flag):

    def decorator(fn):
        def inner(num1, num2):
            if flag == "+":
                print("--正在努力加法计算--")
            elif flag == "-":
                print("--正在努力减法计算--")
            result = fn(num1, num2)
            return result
        return inner

    # 返回装饰器
    return decorator


# 使用装饰器装饰函数
@logging("+")
def add(a, b):
    result = a + b
    return result


@logging("-")
def sub(a, b):
    result = a - b
    return result

result = add(1, 2)
print(result)

result = sub(1, 2)
print(result)

'''
执行结果：
--正在努力加法计算--
3
--正在努力减法计算--
-1
'''


# ################### 类装饰器 ###################
# 类装饰器的介绍：装饰器还有一种特殊的用法就是类装饰器，就是通过定义一个类来装饰函数。
class Check(object):
    def __init__(self, fn):
        # 初始化操作在此完成
        self.__fn = fn

    # 实现__call__方法，表示对象是一个可调用对象，可以像调用函数一样进行调用。
    def __call__(self, *args, **kwargs):
        # 添加装饰功能
        print("请先登陆...")
        self.__fn()


@Check
def comment():
    print("发表评论")
comment()
'''
执行结果：
请先登陆...
发表评论
'''

# 代码说明:
# 1.1@Check 等价于 comment = Check(comment), 所以需要提供一个init方法，并多增加一个fn参数。
# 1.2要想类的实例对象能够像函数一样调用，需要在类里面使用call方法，把类的实例变成可调用对象(callable)，也就是说可以像调用函数一样进行调用。
# 1.3在call方法里进行对fn函数的装饰，可以添加额外的功能。


# 函数式编程
# 其一个特点就是，允许把函数本身作为参数传入另一个函数，还允许返回一个函数！
# 函数本身也可以赋值给变量，即：变量可以指向函数。
f = abs  # 变量f现在已经指向了abs函数本身。
print(f(-10))

# 高阶函数
# 一个函数就可以接收另一个函数作为参数，这种函数就称之为高阶函数。

# map函数
def func(x):
    return x * x


r = map(func, [1,2,3,4])  # map()函数接收两个参数，一个是函数，一个是Iterable
# map将传入的函数依次作用到序列的每个元素，并把结果作为新的Iterator返回。
# Iterator是惰性序列，因此通过list()函数让它把整个序列都计算出来并返回一个list。
print(list(r))

# reduce函数
# reduce把一个函数作用在一个序列[x1, x2, x3, ...]上，这个函数必须接收两个参数。reduce把结果继续和序列的下一个元素做计算。
def fn(x, y):
    return x * 10 + y


res = reduce(fn, [1, 3, 5, 7, 9])
print(res)

# map、reduce函数配合使用将str转为int。
DIGITS = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
def str2int(s):
    def fn1(x, y):
        return x * 10 + y
    def char2num(s):
        return DIGITS[s]
    return reduce(fn1, map(char2num, s))

# 还可以用lambda函数进一步简化成：
# 无需定义fn1这个函数，直接用lambda表达式替换
def char2num(s):
    return DIGITS[s]

def str_to_int(s):
    return reduce(lambda x, y: x * 10 + y, map(char2num, s))

# filter() 函数
# Python内建的filter()函数用于过滤序列。
# filter()把传入的函数依次作用于每个元素，然后根据返回值是True还是False决定保留还是丢弃该元素。
# 注意到filter()函数返回的是一个Iterator，也就是一个惰性序列。
def is_odd(n):
    return n % 2 == 1

res = filter(is_odd, [1, 2, 3, 4, 5, 6])
print(list(res))

def not_empty(s):
    return s and s.strip()

print(list(filter(not_empty, ['A', '', ' B', None, 'C ', '  '])))


# 排序算法
# Python内置的sorted()函数就可以对list进行排序：
print(sorted([36, 5, -12, 9, -21]))
# 此外，sorted()函数也是一个高阶函数，它还可以接收一个key函数来实现自定义的排序，例如按绝对值大小排序：
print(sorted([36, 5, -12, 9, -21], key=abs))
# 给sorted传入key函数，即可实现忽略大小写的排序：
print(sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower))
# 要进行反向排序，不必改动key函数，可以传入第三个参数reverse=True：
print(sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower, reverse=True))
# 按成绩从高到低排序:
L = [('Bob', 75), ('Adam', 92), ('Bart', 66), ('Lisa', 88)]
def by_score(t):
    return -t[1]

L2 = sorted(L, key=by_score)
print(L2)


# 偏函数
# functools.partial：作用就是，把一个函数的某些参数给固定住（也就是设置默认值），返回一个新的函数，调用这个新函数会更简单。
int2 = functools.partial(int, base=2)  # 接收函数对象、*args和**kw这3个参数。入参1是方法名。
# 相当于：
kw = {'base': 2}
int('10010', **kw)

print(int2('1000000'))  # int2方法就是把2进制字符串转为integer，相当于int('char', base=2)
# int2函数，仅仅是把base参数重新设定默认值为2，但也可以在函数调用时传入其他值：
print(int2('1000000', base=10))


# 当传入max2 = functools.partial(max, 10)时，把10作为*args的一部分自动加到左边。
max2 = functools.partial(max, 10)
print(max2(5, 6, 7))
# 相当于：
args = (10, 5, 6, 7)
max(*args)








