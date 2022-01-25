#!/usr/bin/env python
# coding: utf-8

# # 对象注解
# 
# 参考：{daobook}`howto/annotations.html`
# 
# {guilabel}`限制`： Python 3.10 及其以上版本
# 
# ## inspect 用于对象检查
# 
# {mod}`inspect` 模块支持：类型检查、获取源代码、检查类与函数、检查解释器的调用堆栈。
# 
# ### 签名与形参
# 
# - {class}`inspect.Signature(parameters=None, *, return_annotation=Signature.empty)` 代表了一个函数的整体签名。它为每个被函数接受的参数存储一个 {class}`~inspect.Parameter` 对象。可以使用辅助函数 {func}`inspect.signature(obj)` 获取对象 `obj` 的签名。
#     - 可选的 `parameters` 实参是一个 `Parameter` 对象的序列，它被验证以检查是否有名称重复的形参，以及形参的顺序是否正确，即先是仅有位置的形参，然后是有位置或关键字的形参，以及有默认值的形参紧随没有默认值的形参。
#     - 可选的 `return_annotation` 实参，可以是一个任意的 Python 对象，是可调用对象的 "return" 注解。
# - {class}`inspect.Parameter(name, kind, *, default=Parameter.empty, annotation=Parameter.empty)` 代表函数签名中的一个参数。
# 
# ```{note}
# - {class}`~inspect.Signature` 与 {class}`~inspect.Parameter` 对象均是不可变的。分别使用 {func}`Signature.replace` 与 {func}`Parameter.replace` 来制作一个修改的副本。
# - {class}`~inspect.Signature` 与 {class}`~inspect.Parameter` 对象是可提取（picklable）和可散列的。
# ```
# 
# 看一个例子：

# In[22]:


from inspect import signature

def foo(a, *, b:int, **kwargs):
    ...
    
# 获取 `foo` 的签名
sig = signature(foo)
sig


# In[23]:


str(sig) # 转换为字符串


# In[24]:


sig.parameters # 形参名称与相应的 Parameter 对象的有序映射。


# In[25]:


sig.parameters['b'] # 获取给定名称的参数


# In[26]:


sig.parameters['b'].annotation # 获取参数的注解


# In[27]:


# 创建新的签名
new_sig = sig.replace(return_annotation="new return anno")
str(new_sig)


# In[32]:


from inspect import Parameter

# 创建参数实例
param = Parameter('foo', Parameter.KEYWORD_ONLY, default=42)
str(param)


# In[34]:


str(param.replace()) # param 的浅拷贝


# In[35]:


# 添加注解
str(param.replace(default=Parameter.empty, annotation='spam'))


# 参数传值：

# In[38]:


def foo(a, b='ham', *args): ...
ba = signature(foo).bind('spam')

str(ba)


# In[39]:


ba.arguments # 查看实参


# In[41]:


ba.apply_defaults() # 应用默认值
ba.arguments # 查看实参


# ### 注解
# 
# {func}`inspect.get_annotations(obj, *, globals=None, locals=None, eval_str=False)` 计算一个对象的注解 dict。
# 
# `obj` 可以是一个 callable，类，或模块。传入任何其他类型的对象会引发 {exc}`TypeError`。
# 
# {func}`inspect.get_annotations` 每次调用都会返回一个新的 dict；对同一个对象调用两次会返回两个不同但等价的 dict。
# 
# 对象注解属性的最佳实践：
# 
# Python 3.10 以上版本的最佳做法：使用三个参数去调用 {func}`getattr`，比如 `getattr(o, '__annotations__', None)`。

# 
