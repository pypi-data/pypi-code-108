#!/usr/bin/env python
# coding: utf-8

# # `argparse`
# 
# {mod}`argparse`：命令行选项、参数和子命令解析器
# 
# ## 基础
# 
# 我们编写最简单的例子：
# 
# ```{literalinclude} examples/argparse/simple.py
# :language: python
# ```
# 
# 在没有任何选项的情况下运行脚本不会在标准输出显示任何内容。这没有什么用处：

# In[4]:


get_ipython().system('python examples/argparse/simple.py')


# {option}`--help` 选项，也可缩写为 {option}`-h`，是唯一一个可以直接使用的选项（即不需要指定该选项的内容）：

# In[5]:


get_ipython().system('python examples/argparse/simple.py --help')


# 指定其他任何内容都会导致错误。即便如此，我们也能直接得到一条有用的用法信息。

# In[6]:


get_ipython().system('python examples/argparse/simple.py --verbose')


# In[7]:


get_ipython().system('python examples/argparse/simple.py foo')


# ### 位置参数
# 
# 举个例子：
# 
# ```{literalinclude} examples/argparse/echos.py
# :language: python
# ```
# 
# 运行此程序：

# In[9]:


get_ipython().system('python examples/argparse/echos.py')


# 增加了 {meth}`add_argument` 方法，该方法用于指定程序能够接受哪些命令行选项。在这个例子中，我将选项命名为 `echo`，与其功能一致。
# 
# 现在调用我们的程序必须要指定一个选项：

# In[10]:


get_ipython().system('python examples/argparse/echos.py foo')


# 查看帮助信息：

# In[13]:


get_ipython().system('python examples/argparse/echos.py -h')


# 可以给位置参数一些辅助信息：
# 
# ```{literalinclude} examples/argparse/echos_help.py
# :language: python
# ```

# In[14]:


get_ipython().system('python examples/argparse/echos_help.py -h')


# 传入的位置参数选项的值默认是作为字符串传递的，可以修改其为其他类型：
# 
# ```{literalinclude} examples/argparse/square.py
# :language: python
# ```
# 
# 以下是该代码的运行结果：

# In[17]:


get_ipython().system('python examples/argparse/square.py 4')


# 输错类型，会触发异常：

# In[19]:


get_ipython().system("python examples/argparse/square.py '4'")


# 当程序在收到错误的无效的输入时，它甚至能在执行计算之前先退出，还能显示很有帮助的错误信息。
# 
# ### 可选参数
# 
# 下面看看如何添加可选参数：
# 
# ```{literalinclude} examples/argparse/option.py
# :language: python
# ```
# 
# 这一程序被设计为当指定 {command}`--verbosity` 选项时显示某些东西，否则不显示。

# In[20]:


get_ipython().system('python examples/argparse/option.py --verbosity 1')


# In[21]:


get_ipython().system('python examples/argparse/option.py')


# ```{hint}
# 如果一个可选参数没有被使用时，相关变量被赋值为 `None`。
# ```

# In[22]:


get_ipython().system('python examples/argparse/option.py --help')


# 上述例子接受任何整数值作为 {command}`--verbosity` 的参数，但对于简单程序而言，只有两个值有实际意义：`True` 或者 `False`。据此修改代码：
# 
# ```{literalinclude} examples/argparse/option_action.py
# :language: python
# ```
# 
# 现在，这一选项多了一个旗标，而非需要接受一个值的什么东西。我们甚至改变了选项的名字来符合这一思路。注意我们现在指定了一个新的关键词 `action`，并赋值为 `"store_true"`。这意味着，当这一选项存在时，为 `args.verbose` 赋值为 `True`。没有指定时则隐含地赋值为 `False`。

# In[24]:


get_ipython().system('python examples/argparse/option_action.py --verbose')


# In[25]:


get_ipython().system('python examples/argparse/option_action.py --verbose 1')


# In[26]:


get_ipython().system('python examples/argparse/option_action.py -h')


# ### 短选项
# 
# 例如：
# 
# 
# ```{literalinclude} examples/argparse/short.py
# :language: python
# ```
# 
# 
# 效果就像这样：

# In[27]:


get_ipython().system('python examples/argparse/short.py -h')


# In[28]:


get_ipython().system('python examples/argparse/short.py -v')


# ### 结合位置参数和可选参数
# 
# ```{literalinclude} examples/argparse/complex1.py
# :language: python
# ```
# 
# 接着是输出：

# In[1]:


get_ipython().system('python examples/argparse/complex1.py')


# In[2]:


get_ipython().system('python examples/argparse/complex1.py 4')


# In[3]:


get_ipython().system('python examples/argparse/complex1.py 4 --verbose')


# 顺序无关紧要：

# In[4]:


get_ipython().system('python examples/argparse/complex1.py --verbose 4')


# 给程序加上接受多个 `verbosity` 的值，然后实际使用：
# 
# ```{literalinclude} examples/argparse/complex2.py
# :language: python
# ```

# In[5]:


get_ipython().system('python examples/argparse/complex2.py 4')


# In[6]:


get_ipython().system('python examples/argparse/complex2.py 4 -v')


# In[7]:


get_ipython().system('python examples/argparse/complex2.py 4 -v 1')


# In[8]:


get_ipython().system('python examples/argparse/complex2.py 4 -v 2')


# In[9]:


get_ipython().system('python examples/argparse/complex2.py 4 -v 3')


# ## 作为模块使用
# 
# ```python
# # train.py
# import argparse
# 
# 
# def parse_opt(known=False):
#     parser = argparse.ArgumentParser()
#     opt = parser.parse_known_args()[0] if known else parser.parse_args()
#     return opt
# 
# 
# def main(opt):
#     ...
# 
# 
# def run(**kwargs):
#     '''用法（来源于 yolo 代码）
#     import train; train.run(data='coco128.yaml', imgsz=320, weights='yolov5m.pt')
#     '''
#     opt = parse_opt(True)
#     for k, v in kwargs.items():
#         setattr(opt, k, v)
#     main(opt)
# 
# 
# if __name__ == "__main__":
#     opt = parse_opt()
#     main(opt)
# 
# ```
