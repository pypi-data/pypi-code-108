#!/usr/bin/env python
# coding: utf-8

# # 格式字符串字面值
# 
# 格式字符串字面值 或称 f-string 是标注了 `'f'` 或 `'F'` 前缀的字符串字面值。这种字符串可包含替换字段，即以 `{}` 标注的表达式。其他字符串字面值只是常量，格式字符串字面值则是可在运行时求值的表达式。
# 
# 句法格式：
# 
# ```{eval-rst}
# .. productionlist:: python-grammar
#    f_string: (`literal_char` | "{{" | "}}" | `replacement_field`)*
#    replacement_field: "{" `f_expression` ["="] ["!" `conversion`] [":" `format_spec`] "}"
#    f_expression: (`conditional_expression` | "*" `or_expr`)
#                :   ("," `conditional_expression` | "," "*" `or_expr`)* [","]
#                : | `yield_expression`
#    conversion: "s" | "r" | "a"
#    format_spec: (`literal_char` | NULL | `replacement_field`)*
#    literal_char: <any code point except "{", "}" or NULL>
# ```
# 
# 除非字面值标记为原始字符串，否则，与在普通字符串字面值中一样，转义序列也会被解码。
# 
# - 双花括号 `'{{'` 或 `'}}'` 被替换为单花括号，花括号外的字符串仍按字面值处理。
# - 单左花括号 `'{'` 标记以 Python 表达式开头的替换字段。替换字段以右花括号 `'}'` 为结尾。
# - 在表达式后加等于号 `'='`，可在求值后，同时显示表达式文本及其结果（用于调试）。 
# - 用叹号 `'!'` 标记的转换字段。
# - 还可以在冒号 `':'` 后附加格式说明符。
# - 指定了转换符时，表达式求值的结果会先转换，再格式化。转换符 `'!s'` 调用 {func}`str` 转换求值结果，`'!r'` 调用 {func}`repr`，`'!a'` 调用 {func}`ascii`。
# 

# In[1]:


name = "Fred"
f"He said his name is {name!r}."


# In[2]:


f"He said his name is {repr(name)}."  # repr() is equivalent to !r


# In[3]:


import decimal
width = 10
precision = 4
value = decimal.Decimal("12.34567")
f"result: {value:{width}.{precision}}"  # nested fields


# In[5]:


from datetime import datetime

today = datetime(year=2017, month=1, day=27)
f"{today:%B %d, %Y}"  # using date format specifier


# In[6]:


f"{today=:%B %d, %Y}" # using date format specifier and debugging


# In[7]:


number = 1024
f"{number:#0x}"  # using integer format specifier


# In[8]:


foo = "bar"
f"{ foo = }" # preserves whitespace


# In[9]:


line = "The mill's closed"
f"{line = }"


# In[10]:


f"{line = :20}"


# In[11]:


f"{line = !r:20}"


# In[ ]:




