#!/usr/bin/env python
# coding: utf-8

# # 弱引用
# 
# Python 会自动进行内存管理（对大多数对象进行引用计数并使用 {term}`garbage collection` 来清除循环引用）。当某个对象的最后一个引用被移除后不久就会释放其所占用的内存。
# 
# 此方式对大多数应用来说都适用，但偶尔也必须在对象持续被其他对象所使用时跟踪它们。 不幸的是，跟踪它们将创建一个会令其永久化的引用。{mod}`weakref` 模块提供的工具可以不必创建引用就能跟踪对象。当对象不再需要时，它将自动从一个弱引用表中被移除，并为弱引用对象触发一个回调。 典型应用包括对创建开销较大的对象进行缓存：

# In[1]:


import weakref, gc
class A:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)


# In[2]:


a = A(10)                   # create a reference
d = weakref.WeakValueDictionary()
d['primary'] = a            # does not create a reference
print(d['primary'])                # fetch the object if it is still alive

del a                       # remove the one reference
print(gc.collect())                # run garbage collection right away

d['primary']                # entry was automatically removed

