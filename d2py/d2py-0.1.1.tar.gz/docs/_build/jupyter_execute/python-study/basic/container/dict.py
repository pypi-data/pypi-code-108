#!/usr/bin/env python
# coding: utf-8

# # 字典
# 
# 使用 {dfn}`键值对` 的形式创建：

# In[1]:


d = {'wang': '111', 'U': '123'}
d


# 使用 函数 {func}`dict` 创建：
# 
# - 传入键值对位置参数：

# In[2]:


d1 = dict([('A', 1), ('B', 2)])
d1


# - 以关键字参数传入：

# In[3]:


d2 = dict(A=1, B=2)
d2


# 也可以是另一个字典作为参数：

# In[4]:


d3 = dict(d2)
d3


# 或者使用字典解包：

# In[5]:


{**d3, 'c': 3}


# - `len(字典)` 返回字典的项数
# - `in`（类似于序列的用法）

# In[6]:


len(d3) # 字典的大小


# In[7]:


'A' in d3 # 判断是否存在某个元素


# ## 通过键查找或修改
# 
# 示例：

# In[8]:


d = {'wang': '111', 'U': '123'}
d['U'] # 查找元素


# In[9]:


d['wang'] = 111
d # 修改元素


# In[10]:


del d['wang'] # 显式删除
d 


# `clear()`：清除字典中所有的项

# In[11]:


d = {'wang': '111', 'U': '123'}
d.clear()
d


# ## `update` 使用新字典更新旧字典
# 
# 新字典中有而旧字典中没有的项会被加入到旧字典中；新字典中有而旧字典中也有的值会被新字典的值所代替。

# In[12]:


d1 = {'n':'xx','p':'110'}
d2 = {'p':'120','a':'A'}
d1.update(d2)


# In[13]:


d1


# In[14]:


d2


# ## 复制 `copy()`
# 
# 浅复制，得到一个键的指向完全相同原字典的副本。

# In[15]:


d = {'wang':'111','U':[1,2,3,4]}
d1 = d.copy()
d1


# 原地修改原字典 `d`，相应的 `d1` 也会被修改,反之亦然。

# In[16]:


d1['U'].append('lr')
d1


# In[17]:


d


# 如果使用 `deepcopy()` 函数则可以避免上述情况发生。

# In[18]:


from copy import deepcopy

d = {'wang':'111','U':[1,2,3,4]}

d1 = deepcopy(d)
d1


# In[19]:


d


# In[20]:


d1['U'].append('lr')
d1


# In[21]:


d


# ## `get` 方法，查找元素
# 
# 如若元素不存在，可以自定义返回的内容（默认为 `None`）:

# In[22]:


d = {}
d.get('name')


# In[23]:


d


# In[24]:


d['name'] = 'Tom'
d


# In[25]:


d.get('name')


# In[26]:


d.get('phone','Unknown')


# ### `setdefault` 方法，查找元素
# 
# 与 `get` 方法不同的是，当键不存在时，自定义的值和该键会组成一个新项被加入字典。

# In[27]:


d


# In[28]:


d.setdefault('phone','119')


# In[29]:


d


# ## `items()`、`keys()`、`values()` 
# 
# 均以列表的形式返回 `a set-like object`，其中的元素分别为"项"，"键"，"值"。

# In[30]:


d = {'wang':'111', 'U':[1,2,3,4]}
d


# In[31]:


d.items()


# In[32]:


d.keys()


# In[33]:


d.values()


# ## `pop(键)` 
# 
# 返回键对应的值，并删除字典中这个键对应的项。

# In[34]:


d = {'wang':'111','U':[1,2,3,4]}
d.pop('U')


# In[35]:


d


# ### `popitem()` 
# 
# 随机返回字典中的项，并从字典中删除。

# In[36]:


d = {'wang':'111', 'U':[1,2,3,4]}
d.popitem()


# In[37]:


d


# ## 打印乘法表
# 
# ### for 语句

# In[14]:


# 定义乘数
table = {1, 2, 3, 4, 5, 6 ,7, 8, 9}

def multiply(x, y, /):
    return x * y

def print_output(x, y, /):
    out = f"{x} x {y} = {multiply(x, y)}"
    print(out, end='|')


# In[15]:


for x in table:
    for y in table:
        print_output(x, y)
    print('\n')


# 制作可查询的乘法表：

# In[22]:


def output(x, y, /):
    out = f"{x} x {y} = {multiply(x, y):2d}"
    return out


# In[31]:


# 字典推导式
D = {
    f"{x},{y}": output(x, y) 
    for x in table for y in table
}


# In[33]:


D['1,3']


# In[35]:


D['5,3']


# In[ ]:




