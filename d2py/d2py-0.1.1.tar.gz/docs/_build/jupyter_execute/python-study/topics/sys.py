#!/usr/bin/env python
# coding: utf-8

# # 系统相关
# 
# {data}`sys.executable`
# :   一个字符串，提供 Python 解释器的可执行二进制文件的绝对路径，仅在部分系统中此值有意义。如果 Python 无法获取其可执行文件的真实路径，则 `sys.executable` 将为空字符串或 `None`。

# In[1]:


import sys
# IPython 环境
get_ipython().system('{sys.executable} --version')


# In[1]:


# 查看 pip 版本
get_ipython().system('{sys.executable} -m pip --version')

