#!/usr/bin/env python
# coding: utf-8

# # 集合
# 
# {guilabel}`视频`
# 
# <iframe id="Python"
#     title="Python 函数"
#     width="100%"
#     height="600"
#     src="https://developer.hs.net/thread/1865">
# </iframe>
# 
# 集合的元素必须是不可变对象，且元素间有互异性。分为两类：
# 
# - {class}`set`()：可变集合
# - {class}`frozenset`()：不可变集合
# 
# 它们的区别主要在于是否可变，以及写法上面。
# 
# {class}`set` 的定义可以为：

# In[1]:


set('Hello') # 写法 1


# In[2]:


{'H', 'e', 'l', 'o'} # 写法 2


# {class}`frozenset` 的定义：

# In[5]:


frozenset('Hello')


# 下面先以 {class}`set` 为例 Python 如何操作集合的。
# 
# ## 基本操作
# 
# - 支持 {meth}`add` 方法，添加元素

# In[8]:


s = set(['Python','is','a','magic','language'])
s


# In[9]:


s.add('!')
s


# - 支持 函数 {func}`len`、{func}`min`、{func}`max` 运算

# In[17]:


s = {5, 7, 3, 2, 9, 35, 5, 34, 5, 7}
s # 自动去重


# In[18]:


min(s)


# In[19]:


max(s)


# In[20]:


len(s)


# - 支持更新（{meth}`update`）

# In[21]:


a = set([1, 2, 3, 4])
b = set([3, 4, 5, 6])
a.update(b)
a


# - 方法 {meth}`remove` 删除集合中元素

# In[22]:


s = set('hello')
s


# In[23]:


s.remove('h')


# In[24]:


s


# - 若 {meth}`remove` 元素不存在，则会引发错误；而 {meth}`discard` 则不会。

# In[25]:


s.remove('om')


# In[26]:


s.discard('om')


# In[27]:


s


# ## 相等与不相等

# In[28]:


set('Python') == set('python')


# In[29]:


set('Python') != set('python')


# ## 子集 与 超集
# 
# `<`、`<=`、`>`、`>=` 用来判断前面一个集合是否是后面一个集合的严格子集，子集，严格超集，超集。

# In[30]:


set('Hello') < set('HelloWorld')


# In[31]:


set('Hello') <= set('Hello')


# In[32]:


set('Hello') < set('Hello')


# ## 并集（$\bigcup$）使用  `|`

# In[33]:


set('Hello') | set('world')


# ## 交集（$\bigcap$）使用 `&`

# In[34]:


set('Hello') & set('world')


# ## 差集（$-$）使用 `-`

# In[35]:


set('Hello') - set('world')


# ## 对称差使用 ` ^ `

# In[36]:


set([1,2,3,4]) ^ set([3,4,5,6])


# ## 可变与不可变

# In[44]:


a = set((2, 3))

a.remove(2)
a


# In[45]:


a = frozenset((2, 3))

a.remove(2)
a


# ## 集合的特性
# 
# - 如是可变集合（`set`）与不可变集合（`frozenset`）进行运算，得到的新集合的类型与左操作数相同。        
# - 对于可变集合（`set`）可以进行就地修改，支持操作符：`|=`、`&=`、`-=`、`^=`。
# - 集合只能包含不可变的（即可散列的）对象类型。

# In[37]:


a = set('Hello')
a |= set('Python')
a


# In[38]:


a = set('Hello')
a &= set('Python')
a


# In[39]:


a = set('Hello')
a -= set('Python')
a


# In[40]:


a = set('Hello')
a ^= set('Python')
a


# In[41]:


b = set('Hello') | frozenset('Python')
b


# In[42]:


c = frozenset('Python') | set('Hello')
c

