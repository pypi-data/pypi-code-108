#!/usr/bin/env python
# coding: utf-8

# ```{post} 2021/11/24 00:00
# :category: Python
# :tags: basic, udata
# :excerpt: 1
# ```
# 
# # Python `udata` 取数
# 
# 
# 1. 登录平台，[获取Token](https://udata.hs.net/help/292)
# 2. 在数据页面，获取接口名称、请求参数，并查看返回参数及代码示例；
# 3. 编写 Python 脚本，并执行，如下所示：

# In[1]:


# 引入 hs_udata 模块中 set_token 和 stock_list
from hs_udata import set_token, stock_list
# 设置 Token
set_token(token='Xg6Mx3LZo2HACYGJ-ir825yGFKXJwZh5O4hY8g2HDtep4uGTwqYPHupLKIte6Hp_')
data = stock_list()  # 获取 股票列表数据，返回格式为dataframe
data.head()  # 打印数据前5行


# ## 导出数据

# In[2]:


import sys
sys.path.extend(['../../../'])


# In[3]:


from d2py.utils.file import mkdir


# In[5]:


save_root = 'data'
mkdir(save_root)

data.to_excel(f'{save_root}/股票列表.xlsx')                               # 写出Excel文件
data.to_csv(f'{save_root}/股票列表.csv',sep=',',encoding='utf_8_sig')     # 写出CSV文件
data.to_csv(f'{save_root}/股票列表.txt',sep=' ',encoding='utf_8_sig')     # 写出TXT文件


# In[ ]:




