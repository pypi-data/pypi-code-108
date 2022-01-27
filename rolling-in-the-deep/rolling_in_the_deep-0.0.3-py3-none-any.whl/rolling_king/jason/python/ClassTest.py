#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import builtins

# Python 3 可以使用直接使用 super().xxx 代替 super(Class, self).xxx :
class Employee:
    empCount = 0


class Member(object):
    def __init__(self):
        print("This is {0} Constructor.".format("无参"))


member = Member()

class Parent(object):
    def myfunc(self):
        print("This is {0}'s myfunc method.".format("Parent"))

class SubA(Parent):
    def myfunc(self):
        print("This is {0}'s myfunc method.".format("SubA"))
        super().myfunc()
        super(SubA, self).myfunc()

sub = SubA()
sub.myfunc()

class Upper(object):
    def myfunc(self):
        print("This is {0}'s myfunc method.".format("Upper"))
    
# class Child(Parent, SubA):  # 多个基类之间不能存在继承关系否则将有如下错误：
# TypeError: Cannot create a consistent method resolution
# order (MRO) for bases Parent, SubA


class Child(Parent, Upper):
    def __init__(self):
        super(Child, self).__init__()  # 首先找到 Child 的父类（就是类 Parent），然后把类 Child 的对象转换为类 Parent 的对象

    def myfunc(self):
        print("This is {0}'s myfunc method.".format("Child"))
        super(Child, self).myfunc()


child = Child()
child.myfunc()

print(issubclass(Child, Parent))  # Child类 是 Parent的子类
print(isinstance(child, Child))  # child 是 Child类的实例
print(isinstance(child, Parent))  # child 是 Parent类子类的实例
print(isinstance(child, Upper))  # child 是 Upper类子类的实例


# 类的私有属性
# __private_attrs：两个下划线开头，在类内部的方法中使用时 self.__private_attrs。
# 类的私有方法
# __private_method：两个下划线开头，在类的内部调用 self.__private_methods。


# 单下划线、双下划线、头尾双下划线说明：
# __foo__: 定义的是特殊方法，一般是系统定义名字 ，类似 __init__() 之类的。
# _foo: 以单下划线开头的表示的是 protected 类型的变量，即保护类型只能允许其本身与子类进行访问，不能用于 from module import *
# __foo: 双下划线的表示的是私有类型(private)的变量, 只能是允许这个类本身进行访问了。

# Python 中只有模块（module），类（class）以及函数（def、lambda）才会引入新的作用域
# 有四种作用域：
#     L（Local）：最内层，包含局部变量，比如一个函数/方法内部。
#     E（Enclosing）：包含了非局部(non-local)也非全局(non-global)的变量。比如两个嵌套函数，一个函数（或类） A 里面又包含了一个函数 B ，那么对于 B 中的名称来说 A 中的作用域就为 nonlocal。
#     G（Global）：当前脚本的最外层，比如当前模块的全局变量。
#     B（Built-in）： 包含了内建的变量/关键字等。，最后被搜索

# 实例熟悉 与 类属性
# 实例属性属于各个实例所有，互不干扰；
# 类属性属于类所有，所有实例共享一个属性；
# 不要对实例属性和类属性使用相同的名字，否则将产生难以发现的错误。

# 可以给该实例绑定任何属性和方法，这就是动态语言的灵活性
# class Student(object):
#     pass
#
# 然后，尝试给实例绑定一个属性：
# >>> s = Student()
# >>> s.name = 'Michael'
# >>> print(s.name)
# Michael

# 还可以尝试给实例绑定一个方法：
# >>> def set_age(self, age):
#     ...     self.age = age
# ...
# >>> from types import MethodType
# >>> s.set_age = MethodType(set_age, s)
# >>> s.set_age(25)
# >>> s.age
# 25

# 给一个实例绑定的方法，对另一个实例是不起作用的

# 为了给所有实例都绑定方法，可以给class绑定方法：
# >>> def set_score(self, score):
#     ...     self.score = score
# ...
# >>> Student.set_score = set_score
#
# 给class绑定方法后，所有实例均可调用。


# 使用__slots__ 限制某类型的实例可以添加的属性
# 想要限制实例的属性怎么办？Python允许在定义class的时候，定义一个特殊的__slots__变量，来限制该class实例能添加的属性。
# class Student(object):
#     __slots__ = ('name', 'age')
#
# 然后，我们试试：
# >>> s = Student()
# >>> s.name = 'Michael'
# >>> s.age = 25
# >>> s.score = 99  # 试图绑定score将得到AttributeError的错误。

# 使用__slots__要注意，__slots__定义的属性仅对当前类的实例起作用，对继承的子类是不起作用的。


# @property装饰器
# 有没有既能检查参数，又可以用类似属性这样简单的方式来访问类的变量呢？
# Python内置的@property装饰器就是负责把一个方法变成属性调用的。

class Student(object):

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0 or value > 100:
            raise ValueError('score must between 0 ~ 100!')
        self._score = value

# 把一个getter方法变成属性，只需要加上@property就可以了
# @property本身又创建了另一个装饰器@score.setter，负责把一个setter方法变成属性赋值
# >>> s = Student()
# >>> s.score = 60
# >>> s.score
# 60

# 还可以定义只读属性，只定义getter方法，不定义setter方法就是一个只读属性。



# 查看到底预定义了哪些变量:
print(dir(builtins))

# global 关键字
num = 1
def fun1():
    global num  # 需要使用 global 关键字声明
    print(num)
    num = 123
    print(num)


fun1()
print(num)

# 如果要修改嵌套作用域（enclosing 作用域，外层非全局作用域）中的变量则需要 nonlocal 关键字
def outer():
    num = 10
    def inner():
        nonlocal num   # nonlocal关键字声明
        num = num + 100
        print(num)
    inner()
    print(num)


outer()


a = 10
def test(a):  # a 是 number，不可变对象属于值传递，也就是复制a的值传进来，而不是a本身。
    a = a + 1  # 11 = 10 + 1
    print(a)  # 11

test(a)
print(a)  # 10


# 动态语言的“鸭子类型”
# 对于静态语言（例如Java）来说，如果需要传入Animal类型，则传入的对象必须是Animal类型或者它的子类，否则，将无法调用run()方法。
# 对于Python这样的动态语言来说，则不一定需要传入Animal类型。我们只需要保证传入的对象有一个run()方法就可以了


# 获取对象信息。获得一个对象的所有属性和方法
# >>> import types
# >>> def fn():
#     ...     pass
# ...
# >>> type(fn)==types.FunctionType
# True
# >>> type(abs)==types.BuiltinFunctionType
# True
# >>> type(lambda x: x)==types.LambdaType
# True
# >>> type((x for x in range(10)))==types.GeneratorType
# True

# 获得一个对象的所有属性和方法，可以使用dir()函数，它返回一个包含字符串的list
# 调用len()函数试图获取一个对象的长度，实际上，在len()函数内部，它自动去调用该对象的__len__()方法：
# 自己写的类，如果也想用len(myObj)的话，就自己写一个__len__()方法
# 配合getattr()、setattr()以及hasattr()，我们可以直接操作一个对象的状态

# >>> getattr(obj, 'z', 404) # 获取属性'z'，如果不存在，返回默认值404
# 404

# >>> hasattr(obj, 'power') # 有属性'power'吗？
# True
# >>> getattr(obj, 'power') # 获取属性'power'
# <bound method MyObject.power of <__main__.MyObject object at 0x10077a6a0>>
# >>> fn = getattr(obj, 'power') # 获取属性'power'并赋值到变量fn
# >>> fn # fn指向obj.power
# <bound method MyObject.power of <__main__.MyObject object at 0x10077a6a0>>
# >>> fn() # 调用fn()与调用obj.power()是一样的
# 81


# 枚举
from enum import Enum
Month = Enum('Month', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))
print(Month.Jan)
# value属性则是自动赋给成员的int常量，默认从1开始计数。
for name, member in Month.__members__.items():
    print(name, '=>', member, ',', member.value)

# 更精确地控制枚举类型，可以从Enum派生出自定义类:
from enum import Enum, unique
# @unique装饰器可以帮助我们检查保证没有重复值。
@unique
class Weekday(Enum):
    Sun = 0
    Mon = 1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6

day1 = Weekday.Mon
print(day1)
print(Weekday['Tue'])
print(Weekday.Sun.value)
print(day1 == Weekday.Mon)
print(Weekday(1))
print(day1 == Weekday(1))

for name, member in Weekday.__members__.items():
    print(name, '=>', member)


# 使用元类
# 动态语言和静态语言最大的不同，就是函数和类的定义，不是编译时定义的，而是运行时动态创建的。
print(type(Member))
print(type(member))
# class的定义是运行时动态创建的，而创建class的方法就是使用type()函数。
# type()函数既可以返回一个对象的类型，又可以创建出新的类型。
def fn(self, name='world'): # 先定义函数
    print('Hello, %s.' % name)

# 创建一个class对象，type()函数依次传入3个参数：class的名称、继承的父类集合（是一个tuple）、class的方法名称与函数绑定（是一个dict）
Hello = type('Hello', (object,), dict(hello=fn)) # 创建Hello class
h = Hello()
h.hello()
print(type(Hello))  # <class 'type'>
print(type(h))  # <class '__main__.Hello'>

# 除了使用type()动态创建类以外，还可以使用metaclass。
# metaclass，直译为元类。先定义metaclass，就可以创建类，最后创建实例。
# metaclass允许你创建类或者修改类。可以把类看成是metaclass创建出来的“实例”。

# 我们先看一个简单的例子，这个metaclass可以给我们自定义的MyList增加一个add方法：
# 定义ListMetaclass，按照默认习惯，metaclass的类名总是以Metaclass结尾，以便清楚地表示这是一个metaclass：
class ListMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['add'] = lambda self, value: self.append(value)
        print("attrs = ", attrs)  # {'__module__': '__main__', '__qualname__': 'MyList', 'add': <function ListMetaclass.__new__.<locals>.<lambda> at 0x1020b79d0>}
        return type.__new__(cls, name, bases, attrs)

# 有了ListMetaclass，我们在定义类的时候还要指示使用ListMetaclass来定制类，传入关键字参数metaclass：
class MyList(list, metaclass=ListMetaclass):
    pass

# 当我们传入关键字参数metaclass时，魔术就生效了，它指示Python解释器在创建MyList时，要通过ListMetaclass.__new__()来创建，
# 在此，我们可以修改类的定义，比如，加上新的方法，然后，返回修改后的定义。

# __new__()方法接收到的参数依次是：当前准备创建的类的对象、类的名字、类继承的父类集合、类的方法集合。
L = MyList()
L.add(1)  # 普通的list没有add()方法，这个add方法是
L.append(2)
print(L)  # [1, 2]

# ### 通过metaclass来实现ORM框架 ###
# class User(Model):
#     id = IntegerField('id')
#     name = StringField('username')
#     email = StringField('email')
#     password = StringField('password')

# u = User(id=12345, name='Michael', email='test@orm.org', password='my-pwd')

class Field(object):
    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)

class StringField(Field):
    def __init__(self, name):
        super().__init__(name, "varchar(100)")  # Python3 方式

class IntegerField(Field):
    def __init__(self, name):
        super(IntegerField, self).__init__(name, "bigint")  # 通用方式

# 下一步，就是编写最复杂的ModelMetaclass了：




# 建议使用 "import os" 风格而非 "from os import *"。这样可以保证随操作系统不同而有所变化的 os.open() 不会覆盖内置函数 open()。
import os

print(os.getcwd())
os.chdir("/Users/jasonzheng/PycharmProjects/pythonProject/rolling_king/jason")
print(os.getcwd())
os.system("mkdir today")
os.system("touch temp.txt")

# 针对日常的文件和目录管理任务，:mod:shutil 模块提供了一个易于使用的高级接口:
import shutil
shutil.copyfile("temp.txt", "./today/new.txt")
shutil.copy("temp.txt", "./today")

# 文件通配符
# glob模块提供了一个函数用于从目录通配符搜索中生成文件列表:
import glob
list = glob.glob("*.txt")
print(list)





# 测试模块
def average(values):
    """Computes the arithmetic mean of a list of numbers.

    >>> print(average([20, 30, 70]))
    40.0
    """
    return sum(values) / len(values)

import doctest
doctest.testmod()   # 自动验证嵌入测试

a = [10, ]
print(len(a))  # 1

print('%.2f' % 123.444)


# unittest模块
import unittest

class TestStatisticalFunctions(unittest.TestCase):

    def test_average(self):
        self.assertEqual(average([20, 30, 70]), 40.0)
        self.assertEqual(round(average([1, 5, 7]), 1), 4.3)
        self.assertRaises(ZeroDivisionError, average, [])
        self.assertRaises(TypeError, average, 20, 30, 70)

unittest.main() # Calling from the command line invokes all tests

