#!/usr/bin/env python
# coding: utf-8

# # `abc` 抽象基类
# 
# 鸭子类型
# :   一种编程风格（duck-typing），它并不依靠查找对象类型来确定其是否具有正确的接口，而是直接调用或使用其方法或属性（“看起来像鸭子，叫起来也像鸭子，那么肯定就是鸭子。”）由于强调接口而非特定类型，设计良好的代码可通过允许多态替代来提升灵活性。鸭子类型避免使用 {func}`type` 或 {func}`isinstance` 检测。（但要注意鸭子类型可以使用 抽象基类 作为补充。） 而往往会采用 {func}`hasattr` 检测或是 {term}`EAFP` 编程。
# 
# 抽象基类
# :   抽象基类简称 ABC（abstract base class）是对 {dfn}`鸭子类型` 的补充。它提供了一种定义接口的新方式，相比之下其他技巧例如 {func}`hasattr` 显得过于笨拙或有微妙错误（例如使用 **魔术方法**）。ABC 引入了虚拟子类，这种类并非继承自其他类，但却仍能被 {func}`isinstance` 和 {func}`issubclass` 所认可；详见 {mod}`abc` 模块文档。Python 自带许多内置的 ABC 用于实现数据结构（在 {mod}`collections.abc` 模块中）、数字（在 {mod}`numbers` 模块中）、流（在 {mod}`io` 模块中）、导入查找器和加载器（在 {mod}`importlib.abc` 模块中）。你可以使用 {mod}`abc` 模块来创建自己的 ABC。
# 
# {mod}`collections` 模块中有一些派生自 ABC 的具体类；当然这些类还可以进一步被派生。此外，{mod}`collections.abc` 子模块中有一些 ABC 可被用于测试一个类或实例是否提供特定的接口，例如它是否可哈希或它是否为映射等。
# 
# {mod}`abc` 模块提供了一个元类 {class}`~abc.ABCMeta`，可以用来定义抽象类，另外还提供一个工具类 ABC，可以用它以继承的方式定义抽象基类。
# 
# ## `abc.ABCMeta`
# 
# {class}`~abc.ABCMeta` 用于定义抽象基类（ABC）的元类。抽象基类可以像 mix-in 类一样直接被子类继承。你也可以将不相关的具体类（包括内建类）和抽象基类注册为“抽象子类” —— 这些类以及它们的子类会被内建函数 {func}`issubclass` 识别为对应的抽象基类的子类，但是该抽象基类不会出现在其 MRO（Method Resolution Order，方法解析顺序）中，抽象基类中实现的方法也不可调用（即使通过 {func}`super` 调用也不行）。
# 
# 使用 {class}`~abc.ABCMeta` 作为元类创建的类含有如下方法。
# 
# ### `register(subclass)`
# 
# 将 `subclass` 注册为该抽象基类的“虚拟子类”，例如：

# In[3]:


from abc import ABCMeta

class MyABC(metaclass=ABCMeta): ...

MyABC.register(tuple)

assert issubclass(tuple, MyABC)
assert isinstance((), MyABC)


# 你也可以在虚基类中重载 {meth}`~abc.ABCMeta.register` 方法。
# 
# ### `__subclasshook__(subclass)`
# 
# ```{note}
# `__subclasshook__(subclass)` 必须定义为类方法。
# ```
# 
# 检查 `subclass` 是否是该抽象基类的子类。也就是说对于那些你希望定义为该抽象基类的子类的类，你不用对每个类都调用 {meth}`~abc.ABCMeta.register` 方法了，而是可以直接自定义 `issubclass` 的行为。（这个类方法是在抽象基类的 {meth}`~abc.ABCMeta.__subclasscheck__` 方法中调用的。）
# 
# 该方法必须返回 `True`、`False` 或是 `NotImplemented`。如果返回 `True`，`subclass` 就会被认为是这个抽象基类的子类。如果返回 `False`，无论正常情况是否应该认为是其子类，统一视为不是。如果返回 `NotImplemented`，子类检查会按照正常机制继续执行。
# 
# ## `abc.ABC`
# 
# 一个使用 {class}`~abc.ABCMeta` 作为元类的工具类。抽象基类可以通过从 ABC 派生来简单地创建，这就避免了在某些情况下会令人混淆的元类用法，例如：

# In[7]:


from abc import ABC

class MyABC(ABC): ...


# 注意 {class}`~abc.ABC` 的类型仍然是 {class}`~abc.ABCMeta`，因此继承 {class}`~abc.ABC` 仍然需要关注元类使用中的注意事项，比如可能会导致元类冲突的多重继承。
# 
# 此外，{mod}`abc` 模块还提供了一些装饰器。
# 
# ## `@abc.abstractmethod`
# 
# {meth}`abc.abstractmethod` 用于声明抽象方法的装饰器。
# 
# 使用此装饰器要求类的元类是 {class}`~abc.ABCMeta` 或是从该类派生。一个具有派生自 {class}`~abc.ABCMeta` 的元类的类不可以被实例化，除非它全部的抽象方法和特征属性均已被重载。抽象方法可通过任何普通的“super”调用机制来调用。{meth}`~abc.abstractmethod` 可被用于声明特性属性和描述器的抽象方法。
# 
# 动态地添加抽象方法到一个类，或尝试在方法或类被创建后修改其抽象状态等操作仅在使用 {meth}`~abc.update_abstractmethods` 函数时受到支持。{meth}`~abc.abstractmethod` 只会影响使用常规继承所派生的子类；通过 {class}`~abc.ABC` 的 {meth}`~abc.ABCMeta.register` 方法注册的“虚子类”不会受到影响。
# 
# 当 {meth}`~abc.abstractmethod` 与其他方法描述符配合应用时，它应当被应用为最内层的装饰器，如以下用法示例所示：
# 
# ```python
# class C(ABC):
#     @abstractmethod
#     def my_abstract_method(self, ...):
#         ...
#     @classmethod
#     @abstractmethod
#     def my_abstract_classmethod(cls, ...):
#         ...
#     @staticmethod
#     @abstractmethod
#     def my_abstract_staticmethod(...):
#         ...
# 
#     @property
#     @abstractmethod
#     def my_abstract_property(self):
#         ...
#     @my_abstract_property.setter
#     @abstractmethod
#     def my_abstract_property(self, val):
#         ...
# 
#     @abstractmethod
#     def _get_x(self):
#         ...
#     @abstractmethod
#     def _set_x(self, val):
#         ...
#     x = property(_get_x, _set_x)
# ```
# 
# 为了能正确地与抽象基类机制实现互操作，描述符必须使用 `__isabstractmethod__` 将自身标识为抽象的。通常，如果被用于组成描述符的任何方法都是抽象的则此属性应当为 `True`。例如，Python 的内置 `property` 所做的就等价于：
# 
# ```python
# class Descriptor:
#     ...
#     @property
#     def __isabstractmethod__(self):
#         return any(getattr(f, '__isabstractmethod__', False) for
#                    f in (self._fget, self._fset, self._fdel))
# ```
# 
# 可以定义了一个只读特征属性：
# 
# ```python
# class C(ABC):
#     @property
#     @abstractmethod
#     def my_abstract_property(self):
#         ...
# ```
# 
# 也可以通过适当地将一个或多个下层方法标记为抽象的来定义可读写的抽象特征属性：
# 
# ```python
# class C(ABC):
#     @property
#     def x(self):
#         ...
# 
#     @x.setter
#     @abstractmethod
#     def x(self, val)
# ```
# 
# 如果只有某些组件是抽象的，则只需更新那些组件即可在子类中创建具体的特征属性：
# 
# ```python
# class D(C):
#     @C.x.setter
#     def x(self, val):
#         ...
# ```
# 
# {mod}`abc` 模块还提供了一些函数。
# 
# ## `abc.get_cache_token()`
# 
# 你可以使用 {func}`~abc.get_cache_token` 函数来检测对 {func}`~abc.ABCMeta.register` 的调用。
# 
# - 返回当前抽象基类的缓存令牌。
# - 此令牌是一个不透明对象（支持相等性测试），用于为虚子类标识抽象基类缓存的当前版本。
# - 此令牌会在任何 {class}`~abc.ABC` 上每次调用 {func}`~abc.ABCMeta.register` 时发生更改。
# 
# 为演示 `__subclasshook__(subclass)` 的概念，请看以下定义 ABC 的示例：

# In[8]:


from abc import ABC, abstractmethod

class Foo:
    def __getitem__(self, index):
        ...
    def __len__(self):
        ...
    def get_iterator(self):
        return iter(self)

class MyIterable(ABC):

    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    def get_iterator(self):
        return self.__iter__()

    @classmethod
    def __subclasshook__(cls, C):
        if cls is MyIterable:
            if any("__iter__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

MyIterable.register(Foo)


# ABC `MyIterable` 定义了标准的迭代方法 {meth}`~iterator.__iter__` 作为一个抽象方法。这里给出的实现仍可在子类中被调用。{meth}`get_iterator` 方法也是 `MyIterable` 抽象基类的一部分，但它并非必须被非抽象派生类所重载。
# 
# 这里定义的 {meth}`__subclasshook__` 类方法指明了任何在其 {attr}`~object.__dict__` （或在其通过 {attr}`~class.__mro__` 列表访问的基类）中具有 {meth}`~iterator.__iter__` 方法的类也都会被视为 `MyIterable`。
# 
# 最后，末尾行使得 `Foo` 成为 `MyIterable` 的一个虚子类，即使它没有定义 {meth}`~iterator.__iter__` 方法（它使用了以 {func}`__len__` 和 `__getitem__()` 术语定义的旧式可迭代对象协议）。请注意这将不会使 {meth}`get_iterator` 成为 `Foo` 的一个可用方法，它是被另外提供的。
# 
# ## `abc.update_abstractmethods(cls)`
# 
# `abc.update_abstractmethods(cls)` 重新计算一个抽象类的抽象状态的函数。如果一个类的抽象方法在类被创建后被实现或被修改则应当调用此函数。通常，此函数应当在一个类装饰器内部被调用。
# 
# - 返回 `cls`，使其能够用作类装饰器。
# - 如果 `cls` 不是 {class}`abc.ABCMeta` 的子类，则不做任何操作。

# 
