#!/usr/bin/env python
# coding: utf-8

# # 元类
# 
# **元类** 用于创建和管理类（`class`）。

# In[2]:


class Foo: ...

isinstance(Foo, object)


# `Foo` 是由 {class}`type` 创建的：

# In[3]:


type(Foo)


# ```{note}
# 使用 `class` 语句创建新类：
# 
# 1. 类主体将作为其私有字典内的一系列语句执行。
# 2. 类内语句的执行过程与正常代码执行过程相同，只是增加了会在私有成员（名称以 `__` 开头）上发生的名称变形。
# 3. 类的名称、基类类别和字典将传递给元类的构造函数，以构建相应的类对象。
# ```
# 
# - 可以显式地指定元类：
# 
#     ```python
#     class Foo(metaclass=type): ...
#     ```
# 
# - 如果没有显式指定元类，`class` 语句将检查基类元组（如果存在）中的第一项。
# - 如果没有指定基类，`class` 语句将检查全局变量 `__metaclass__` 是否存在。比如：
# 
#     ```python
#     __metaclass__ = type
#     class Foo: ...
#     ```
# 
# 在 Python3 中默认元类是 `type`。
