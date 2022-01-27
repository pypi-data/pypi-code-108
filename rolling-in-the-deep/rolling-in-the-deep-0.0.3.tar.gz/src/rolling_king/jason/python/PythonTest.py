# -*- coding: UTF-8 -*-

import math
# 自定义函数
# def functionname( parameters ):
#    "函数_文档字符串"
#    function_suite
#    return [expression]

# 可更改(mutable)与不可更改(immutable)对象
# 在 python 中，strings, tuples, 和 numbers 是不可更改的对象，而 list,dict 等则是可以修改的对象。
#  不可变类型：变量赋值 a=5 后再赋值 a=10，这里实际是新生成一个 int 值对象 10，再让 a 指向它，而 5 被丢弃，不是改变a的值，相当于新生成了a。
#  可变类型：变量赋值 la=[1,2,3,4] 后再赋值 la[2]=5 则是将 list la 的第三个元素值更改，本身la没有动，只是其内部的一部分值被修改了。
#
# python 函数的参数传递：
#  不可变类型：类似 c++ 的值传递，如 整数、字符串、元组。如fun（a），传递的只是a的值，没有影响a对象本身。比如在 fun（a）内部修改 a 的值，只是修改另一个复制的对象，不会影响 a 本身。
#  可变类型：类似 c++ 的引用传递，如 列表，字典。如 fun（la），则是将 la 真正的传过去，修改后fun外部的la也会受影响
# 不可变类型 是 值传递；可变类型 是 引用传递。

def ChangeInt(a):
    a = 10


b = 2
ChangeInt(b)
print("b = ", b)  # 结果是 2，因为不可变类型 是 值传递。


# 可写函数说明
def changeme(mylist):
    """修改传入的列表"""
    mylist.append([1, 2, 3, 4])
    print("函数内取值: ", mylist)
    return


# 调用changeme函数
mylist = [10, 20, 30]
changeme(mylist)
print("函数外取值: ", mylist)
print(len(mylist))

# 参数种类
# 正式参数类型：必选参数、默认参数、可变参数、命名关键字参数、关键字参数 共计5种。（方法定义时，也按此顺序！）
# 必备参数须以正确的顺序传入函数。调用时的数量必须和声明时的一样。
# changeme()  # 将会报错，缺少必要参数： changeme() missing 1 required positional argument: 'mylist'

# 使用关键字参数允许函数调用时参数的顺序与声明时不一致，因为 Python 解释器能够用参数名匹配参数值。
def printinfo(name, age):
    "打印任何传入的字符串"
    print("Name: ", name)
    print("Age ", age)
    return


# 调用printinfo函数
printinfo(age=50, name="miki")

# 默认参数的值如果没有传入，则被认为是默认值。
def printinfo1(name, age=0):
    """打印任何传入的字符串"""
    print("Name: ", name)
    print("Age ", age)
    return

printinfo1("Jason")
printinfo1(name="Jason")
printinfo1(age=10, name="Jason")

# 加了星号（*）的变量名会存放所有未命名的变量参数。不定长参数, 声明时不会命名。
def printinfo(arg1, *vartuple):
   "打印任何传入的参数"
   print("输出: ", arg1)
   for var in vartuple:
      print(var)


printinfo(10)
printinfo(70, 60, 50)
nums = [1,2,3]
printinfo(nums)  # 传入一个list，相当于传了一个参数，对应方法的arg1；没有传入后面的可变参数
printinfo(*nums)  # 在入参list前添加*，变成可变参数，就是list的各个元素，相当于传入了三个参数。



# *args 和 **kwargs 主要用于函数定义。
# 你可以将不定数量的参数传递给一个函数。不定的意思是：预先并不知道, 函数使用者会传递多少个参数给你, 所以在这个场景下使用这两个关键字。其实并不是必须写成 *args 和 **kwargs。  *(星号) 才是必须的. 你也可以写成 *ar  和 **k 。而写成 *args 和**kwargs 只是一个通俗的命名约定。
# python函数传递参数的方式有两种：位置参数（positional argument）、关键词参数（keyword argument）
#
# *args 与 **kwargs 的区别，两者都是 python 中的可变参数：
#
#     *args 表示任何多个无名参数（可变参数），它本质是一个 tuple
#     **kwargs 表示关键字参数，它本质上是一个 dict
#
# 如果同时使用 *args 和 **kwargs 时，必须 *args 参数列要在 **kwargs 之前。

def person(name, age, **kw):
    print('name:', name, 'age:', age, 'other:', kw)


person("zy", 30, city='Beijing')
extra = {'city': 'Beijing', 'job': 'Engineer'}
person("smm", 28, **extra)  # 必须通过**将dict转为关键字参数。

# 命名关键字参数
# 限制关键字参数的名字，就可以用命名关键字参数
# （1）在没有可变参数的情况下，命名关键字参数需要一个特殊分隔符*，*后面的参数被视为命名关键字参数
def person1(name, age, *, city, job):
    print(name, age, city, job)

# （2）在存在可变参数的情况下，可变参数后面跟着的命名关键字参数就不再需要一个特殊分隔符*了。
def person2(name, age, *args, city, job):
    print(name, age, args, city, job)


# 对于任意函数，都可以通过类似func(*args, **kw)的形式调用它，无论它的参数是如何定义的。
def f1(a, b, c=0, *args, **kw):
    print('a =', a, 'b =', b, 'c =', c, 'args =', args, 'kw =', kw)

def f2(a, b, c=0, *, d, **kw):
    print('a =', a, 'b =', b, 'c =', c, 'd =', d, 'kw =', kw)

args = (1, 2, 3, 4)
kw = {'d': 99, 'x': '#'}
f1(*args, **kw)  # a = 1 b = 2 c = 3 args = (4,) kw = {'d': 99, 'x': '#'}

args = (1, 2, 3)
kw = {'d': 88, 'x': '#'}
f2(*args, **kw)  # a = 1 b = 2 c = 3 d = 88 kw = {'x': '#'}


# 匿名函数：python 使用 lambda 来创建匿名函数。
# lambda [arg1 [,arg2,.....argn]]:expression
# 可写函数说明
sum = lambda arg1, arg2: arg1 + arg2

# 调用sum函数
print("相加后的值为 : ", sum(10, 20))
print("相加后的值为 : ", sum(20, 20))

# 变量作用域：全局变量 和 局部变量
total = 0  # 这是一个全局变量

# 可写函数说明
def sum(arg1, arg2):
    # 返回2个参数的和."
    total = arg1 + arg2  # total在这里是局部变量, 是一个定义的新变量（局部变量且名为total）
    print("函数内是局部变量 : ", total)  # 30
    return total


# 调用sum函数
sum(10, 20)
print("函数外是全局变量 : ", total)  # 0

total = sum(10, 20)
print("函数外是全局变量 : ", total)  # 30


# Python 模块
# Python 模块(Module)，是一个 Python 文件，以 .py 结尾，包含了 Python 对象定义和Python语句。
# 请注意，每一个包目录下面都会有一个__init__.py的文件，这个文件是必须存在的，否则，Python就把这个目录当成普通目录，而不是一个包。
# __init__.py可以是空文件，也可以有Python代码，因为__init__.py本身就是一个模块，而它的模块名就是mycompany。
# 类似的，可以有多级目录，组成多级层次的包结构。比如如下的目录结构：
# mycompany
# ├─ web
# │  ├─ __init__.py
# │  ├─ utils.py
# │  └─ www.py
# ├─ __init__.py
# ├─ abc.py
# └─ utils.py

# 模块的引入
# 模块定义好后，我们可以使用 import 语句来引入模块，语法如下：
# import module1[, module2[,... moduleN]]
# 当解释器遇到 import 语句，如果模块在当前的搜索路径就会被导入。
# 搜索路径是一个解释器会先进行搜索的所有目录的列表。
# 需要把import命令放在脚本的顶端.
# 引入模块后，通过 模块名.函数名 方式调用模块中的函数。

# from…import 语句
# Python 的 from 语句让你从模块中导入一个指定的部分到当前命名空间中。语法如下：
# from modname import name1[, name2[, ... nameN]]
# from modname import *

# 自己创建模块时要注意命名，不能和Python自带的模块名称冲突。
# 例如，系统自带了sys模块，自己的模块就不可命名为sys.py，否则将无法导入系统自带的sys模块。

# sys模块有一个argv变量，用list存储了命令行的所有参数。argv至少有一个元素，因为第一个参数永远是该.py文件的名称。
# 在命令行运行hello模块文件时，Python解释器把一个特殊变量__name__置为__main__，
# 而如果在其他地方导入该hello模块时，if判断将失效。
# $ python hello.py Michael 的 参数Michael可以被sys.argv这个list获取到。

# 搜索路径
# 当你导入一个模块，Python 解析器对模块位置的搜索顺序是：
# 1、当前目录
# 2、如果不在当前目录，Python 则搜索在 shell 变量 PYTHONPATH 下的每个目录。
# 3、如果都找不到，Python会察看默认路径。UNIX下，默认路径一般为/usr/local/lib/python/。
# 模块搜索路径存储在 system 模块的 sys.path 变量中。变量里包含当前目录，PYTHONPATH和由安装过程决定的默认目录。

# PYTHONPATH 变量
# 作为环境变量，PYTHONPATH 由装在一个列表里的许多目录组成。PYTHONPATH 的语法和 shell 变量 PATH 的一样。


# 命名空间和作用域
# 变量是拥有匹配对象的名字（标识符）。命名空间是一个包含了变量名称们（键）和它们各自相应的对象们（值）的字典。
# 一个 Python 表达式可以访问局部命名空间和全局命名空间里的变量。如果一个局部变量和一个全局变量重名，则局部变量会覆盖全局变量。
# 每个函数都有自己的命名空间。类的方法的作用域规则和通常函数的一样。
# Python 会智能地猜测一个变量是局部的还是全局的，它假设任何在函数内赋值的变量都是局部的。
# 因此，如果要给函数内的全局变量赋值，必须使用 global 语句。
# global VarName 的表达式会告诉 Python， VarName 是一个全局变量，这样 Python 就不会在局部命名空间里寻找这个变量了。
Money = 2000
def AddMoney():
   # 想改正代码就取消以下注释:
   global Money
   Money = Money + 1


print(Money)
AddMoney()
print(Money)

# dir()函数
# dir() 函数一个排好序的字符串列表，内容是一个模块里定义过的名字。
# 返回的列表容纳了在一个模块里定义的所有模块，变量和函数。获得一个对象的所有属性和方法。
content = dir(math)
print(content)
# 特殊字符串变量__name__指向模块的名字:
print(math.__name__)
# __file__指向该模块的导入文件名:
print(math.__file__)

# globals() 和 locals() 函数
# 根据调用地方的不同，globals() 和 locals() 函数可被用来返回全局和局部命名空间里的名字。
# 如果在函数内部调用 locals()，返回的是所有能在该函数里访问的命名。
# 如果在函数内部调用 globals()，返回的是所有在该函数里能访问的全局名字。
# 两个函数的返回类型都是字典。所以名字们能用 keys() 函数摘取。
def func():
    a = 1
    b = 2
    print(globals())
    print(globals().keys())
    print(locals())
    print(locals().keys())


func()

# reload() 函数
# 当一个模块被导入到一个脚本，模块顶层部分的代码只会被执行一次。该函数会重新导入之前导入过的模块。
# 语法：reload(module_name), 入参不是字符串，就是module_name，譬如：reload(math)

# Python中的包
# 包是一个分层次的文件目录结构，它定义了一个由模块及子包，和子包下的子包等组成的 Python 的应用环境。
# 简单来说，包就是文件夹，但该文件夹下必须存在 __init__.py 文件, 该文件的内容可以为空。__init__.py 用于标识当前文件夹是一个包。


# Python 文件I/O
# 读取键盘输入
# raw_input([prompt]) 函数从标准输入读取一个行，并返回一个字符串（去掉结尾的换行符）：
# 但是 input 可以接收一个Python表达式作为输入，并将运算结果返回


# 打开和关闭文件
# open 函数: 你必须先用Python内置的open()函数打开一个文件，创建一个file对象，相关的方法才可以调用它进行读写
# file object = open(file_name [, access_mode][, buffering])
fileObj = open("/Users/jasonzheng/Desktop/CAT告警.txt", mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
print("文件名: ", fileObj.name)
print("是否已关闭 : ", fileObj.closed)
print("访问模式 : ", fileObj.mode)
# print("末尾是否强制加空格 : ", fileObj.softspace)
firstLine = fileObj.readline()
print(firstLine)
# tell()方法告诉你文件内的当前位置, 换句话说，下一次的读写会发生在文件开头这么多字节之后。
# seek（offset [,from]）方法改变当前文件的位置。
# 查找当前位置
position = fileObj.tell()
print("当前文件位置 : ", position)
print(fileObj.seek(35, 0))
print(fileObj.read(5))

# 重命名和删除文件
# Python的os模块提供了帮你执行文件处理操作的方法
# import os
# os.renames("oldfilename.txt", "newfilename.txt")
# os.remove("existfilename.txt")
# os.mkdir("newdirectory")
# os.chdir("newdirname")
# print(os.getcwd())
# os.rmdir('newdirname')

if fileObj.closed :
    print("File has been already closed.")
else:
    fileObj.close()
    print("File is closed now.")

print(fileObj.closed)


# Python 异常处理
# 什么是异常？
# 异常即是一个事件，该事件会在程序执行过程中发生，影响了程序的正常执行。
# 一般情况下，在Python无法正常处理程序时就会发生一个异常。
# 异常是Python对象，表示一个错误。
# 当Python脚本发生异常时我们需要捕获处理它，否则程序会终止执行。

# 以下为简单的try....except...else的语法：

# try:
# <语句>        #运行别的代码
# except <名字>：
# <语句>        #如果在try部份引发了'name'异常
# except <名字>，<数据>:
# <语句>        #如果引发了'name'异常，获得附加的数据
# else:
# <语句>        #如果没有异常发生
try:
    fh = open("testfile", "w")
    fh.write("这是一个测试文件，用于测试异常!!")
except IOError:
    print("Error: 没有找到文件或读取文件失败")
else:
    print("内容写入文件成功")
    fh.close()


def exp_func():
    print("raise IOError exception")
    raise IOError("my io error")


try:
    print("try body")
    exp_func()
except IOError as err:
    print("get IOError exception")
    print("OS error: {0}".format(err))
    # raise #抛出
else:
    print("else block")
finally:
    print("finally block")
