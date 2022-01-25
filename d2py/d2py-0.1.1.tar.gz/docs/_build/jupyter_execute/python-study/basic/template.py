#!/usr/bin/env python
# coding: utf-8

# # 模板
# 
# {mod}`string` 模块提供了通用的 {class}`string.Template` 类，具有适用于最终用户的简化语法。它允许用户在不更改应用逻辑的情况下自定义应用。
# 
# 实现方式：利用占位符 `$` 加上合法的 Python 标识符构成。一旦使用 `{ }` 将占位符括起来，就可以在后面直接跟上更多的字面和数字而无需空格分隔。`$` 的语义由 `$$` 提供转义。

# In[1]:


from string import Template
t = Template('${village}folk send $$10 to $cause.')
t.substitute(village='Nottingham', cause='the ditch fund')


# 如果在字典或关键字参数中未提供某个占位符的值，那么 {meth}`string.Template.substitute` 方法将抛出 {exc}`KeyError`。对于 mail-merge 风格的应用，用户提供的数据有可能是不完整的，此时使用 {meth}`string.Template.safe_substitute` 方法更加合适 —— 如果数据缺失，它会直接将占位符原样保留。

# In[2]:


t = Template('Return the $item to $owner.')
d = dict(item='unladen swallow')
t.substitute(d)


# In[3]:


t.safe_substitute(d)


# `Template` 的子类可以自定义分隔符。例如，以下是某个照片浏览器的批量重命名功能，采用了百分号作为日期、照片序号和照片格式的占位符：
# 
# ```python
# import time, os.path
# from string import Template
# 
# photofiles = ['img_1074.jpg', 'img_1076.jpg', 'img_1077.jpg']
# class BatchRename(Template):
#     delimiter = '%'
# fmt = input('Enter rename style (%d-date %n-seqnum %f-format):  ')
# 
# t = BatchRename(fmt)
# date = time.strftime('%d%b%y')
# for i, filename in enumerate(photofiles):
#     base, ext = os.path.splitext(filename)
#     newname = t.substitute(d=date, n=i, f=ext)
#     print('{0} --> {1}'.format(filename, newname))
# ```
# 
# 模板的另一个应用是将程序逻辑与多样的格式化输出细节分离开来。这使得对 XML 文件、纯文本报表和 HTML 网络报表使用自定义模板成为可能。

# 
