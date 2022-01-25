#!/usr/bin/env python
# coding: utf-8

# # 内置常量
# 
# - 布尔值：{data}`False` （表示逻辑值为假）、{data}`True` （表示逻辑值为真）
# - 空值：{data}`None`
# - {data}`NotImplemented`
# - {data}`Ellipsis`：与省略号字面值 `...` 相同。
# - {data}`__debug__`
# 
# 名称 {data}`None`，{data}`False`，{data}`True` 和 {data}`__debug__` 无法重新赋值（赋值给它们，即使是属性名，将引发 {exc}`SyntaxError`），所以它们可以被认为是“真正的”常量。
# 
# 演示如下：

# In[ ]:


False = 'e'


# In[ ]:


True = 5


# In[ ]:


None  = 'w'


# In[ ]:


__debug__ = 2


# ## {data}`NotImplemented`
# 
# {data}`NotImplemented` 是 {data}`types.NotImplementedType` 类型的唯一实例。

# In[1]:


type(NotImplemented)


# 作为布尔值来解读 `NotImplemented` 已被弃用。虽然它目前会被解读为真值，但将同时发出 : {exc}`DeprecationWarning`。它将在未来的 Python 版本中引发 {exc}`TypeError`。

# In[2]:


bool(NotImplemented)


# 当二元（或就地）运算返回 `NotImplemented` 时，解释器将尝试对另一种类型（或其他一些回滚操作，取决于运算符）实施反射操作。如果所有尝试都返回 `NotImplemented`，则解释器将引发适当的异常。错误返回的 `NotImplemented` 将导致误导性错误消息或返回到 Python 代码中的 `NotImplemented` 值。

# In[1]:


from demo.a import A, B


# In[3]:


a = A(4)
b = B(4)


# In[4]:


a == b


# In[5]:


b == a


# In[ ]:




