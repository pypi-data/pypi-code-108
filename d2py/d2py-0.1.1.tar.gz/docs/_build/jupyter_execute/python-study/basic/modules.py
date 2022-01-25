#!/usr/bin/env python
# coding: utf-8

# # 模块
# 
# 随着程序越来越多，仅仅靠单个文件管理代码是很不好的行为。可以把程序分成不同逻辑单元并放入不同的文件（一般后缀为 `.py`）中，这些文件在 Python 中称为 **模块**。
# 
# 模块中的定义可以导入到其他模块或主模块（在顶层和计算器模式下，执行脚本中可访问的变量集）。
# 
# 在模块内部，通过全局变量 `__name__` 可以获取模块名（即字符串）。
# 
# 例如，用文本编辑器在目录 `examples/modules/` 下创建 `fibo.py` 文件，输入以下内容：
# 
# ```{literalinclude} examples/modules/fibo.py
# :language: python
# ```
# 
# 用以下命令导入该模块：

# In[1]:


get_ipython().run_line_magic('cd', 'examples/modules')


# In[2]:


import fibo


# 这项操作不直接把 `fibo` 函数定义的名称导入到当前符号表，只导入模块名 fibo 。要使用模块名访问函数：

# In[3]:


fibo.fib(1000)


# In[4]:


fibo.fib2(1000)


# In[5]:


fibo.__name__


# 如果经常使用某个函数，可以把它赋值给局部变量：

# In[6]:


fib = fibo.fib
fib(500)


# ## 模块详解
# 
# 模块包含可执行语句及函数定义。这些语句用于初始化模块，且仅在 `import` 语句首次遇到模块名时执行。（文件作为脚本运行时，也会执行这些语句。）
# 
# 模块有自己的私有符号表，用作模块中所有函数的全局符号表。因此，在模块内使用全局变量时，不用担心与用户定义的全局变量发生冲突。另一方面，可以用与访问模块函数一样的标记法，访问模块的全局变量，`modname.itemname`。
# 
# 可以把其他模块导入模块。按惯例，所有 {keyword}`import` 语句都放在模块（或脚本）开头，但这不是必须的。导入的模块名存在导入模块的全局符号表里。
# 
# `import` 语句有一个变体，可以直接把模块里的名称导入到另一个模块的符号表。例如：

# In[7]:


from fibo import fib, fib2
fib(500)


# 这段代码不会把模块名导入到局部符号表里。
# 
# 还有一种变体可以导入模块内定义的所有名称：

# In[8]:


from fibo import *
fib(500)


# 这种方式会导入所有不以下划线（`_`）开头的名称。大多数情况下，不要用这个功能，这种方式向解释器导入了一批未知的名称，可能会覆盖已经定义的名称。
# 
# 模块名后使用 {keyword}`as` 时，直接把 `as` 后的名称与导入模块绑定。

# In[9]:


import fibo as fib
fib.fib(500)


# 与 `import fibo` 一样，这种方式也可以有效地导入模块，唯一的区别是，导入的名称变成 `fib`。
# 
# {keyword}`from` 中也可以使用这种方式，效果类似：

# In[10]:


from fibo import fib as fibonacci
fibonacci(500)


# ```{note}
# 为了保证运行效率，每次解释器会话只导入一次模块。如果更改了模块内容，必须重启解释器；仅交互测试一个模块时，也可以使用 {func}`importlib.reload()`，例如 `import importlib; importlib.reload(modulename)`。
# ```
# 
# ## 基础
# 
# ### 以脚本方式执行模块
# 
# 可以用以下方式运行 Python 模块：
# 
# ```sh
# python fibo.py <arguments>
# ```
# 
# 这项操作将执行模块里的代码，和导入模块一样，但会把 `__name__` 赋值为 `"__main__"`。 也就是把下列代码添加到模块末尾：
# 
# ```python
# if __name__ == "__main__":
#     import sys
#     fib(int(sys.argv[1]))
# ```
# 
# 既可以把这个文件当脚本使用，也可以用作导入的模块，因为，解析命令行的代码只有在模块以 “`main`” 文件执行时才会运行：

# In[11]:


get_ipython().system('python fibo.py 50')


# 导入模块时，不运行这些代码：

# In[12]:


import fibo


# 这种操作常用于为模块提供便捷用户接口，或用于测试（把模块当作执行测试套件的脚本运行）。
# 
# ### 模块搜索路径
# 
# 导入 `spam` 模块时，解释器首先查找名为 `spam` 的内置模块。如果没找到，解释器再从 {data}`sys.path` 变量中的目录列表里查找 `spam.py` 文件。{data}`sys.path` 初始化时包含以下位置：
# 
# - 输入脚本的目录（或未指定文件时的当前目录）。
# - {envvar}`PYTHONPATH` （目录列表，与 shell 变量 {envvar}`PATH` 的语法一样）。
# - 依赖于安装的默认值（按惯例包括一个 `site-packages` 目录，由 {mod}`site` 模块处理）。
# 
# ```{note}
# 在支持 symlink 的文件系统中，输入脚本目录是在追加 symlink 后计算出来的。换句话说，包含 symlink 的目录并 没有 添加至模块搜索路径。
# ```
# 
# 初始化后，Python 程序可以更改 {data}`sys.path`。运行脚本的目录在标准库路径之前，置于搜索路径的开头。即，加载的是该目录里的脚本，而不是标准库的同名模块。 除非刻意替换，否则会报错。
# 
# ### “已编译的” Python 文件
# 
# 为了快速加载模块，Python 把模块的编译版缓存在 `__pycache__` 目录中，文件名为 `module.version.pyc`，`version` 对编译文件格式进行编码，一般是 Python 的版本号。例如，CPython 的 3.3 发行版中，`spam.py` 的编译版本缓存为 `__pycache__/spam.cpython-33.pyc`。使用这种命名惯例，可以让不同 Python 发行版及不同版本的已编译模块共存。
# 
# Python 对比编译版本与源码的修改日期，查看它是否已过期，是否要重新编译，此过程完全自动化。此外，编译模块与平台无关，因此，可在不同架构系统之间共享相同的支持库。
# 
# Python 在两种情况下不检查缓存。其一，从命令行直接载入模块，只重新编译，不存储编译结果；其二，没有源模块，就不会检查缓存。为了支持无源文件（仅编译）发行版本， 编译模块必须在源目录下，并且绝不能有源模块。
# 
# ```{admonition} 给专业人士的一些小建议
# :class: tip
# 
# 1. 在 Python 命令中使用 {option}`-O` 或 {option}`-OO` 开关，可以减小编译模块的大小。`-O` 去除断言语句，`-OO` 去除断言语句和 `__doc__` 字符串。有些程序可能依赖于这些内容，因此，没有十足的把握，不要使用这两个选项。“优化过的” 模块带有 `opt-` 标签，并且文件通常会一小些。将来的发行版或许会改进优化的效果。
# 2. 从 .pyc 文件读取的程序不比从 .py 读取的执行速度快，.pyc 文件只是加载速度更快。
# 3. {mod}`compileall` 模块可以为一个目录下的所有模块创建 `.pyc` 文件。
# 
# 本过程的细节及决策流程图，详见 {pep}`3147`。
# ```
# 
# ## 标准模块
# 
# Python 自带一个标准模块的库，它在 Python 库参考（此处以下称为"库参考" ）里另外描述。 一些模块是内嵌到编译器里面的， 它们给一些虽并非语言核心但却内嵌的操作提供接口，要么是为了效率，要么是给操作系统基础操作例如系统调入提供接口。 这些模块集是一个配置选项， 并且还依赖于底层的操作系统。 例如，{mod}`winreg` 模块只在 Windows 系统上提供。一个特别值得注意的模块 {mod}`sys`，它被内嵌到每一个 Python 编译器中。`sys.ps1` 和 `sys.ps2` 变量定义了一些字符，它们可以用作主提示符和辅助提示符:

# In[13]:


import sys

sys.ps1


# In[14]:


sys.ps2


# In[15]:


sys.ps1 = 'C> '


# 只有解释器用于交互模式时，才定义这两个变量。
# 
# 变量 {data}`sys.path` 是字符串列表，用于确定解释器的模块搜索路径。该变量以环境变量 {envvar}`PYTHONPATH` 提取的默认路径进行初始化，如未设置 {envvar}`PYTHONPATH`，则使用内置的默认路径。可以用标准列表操作修改该变量：
# 
# ```python
# import sys
# sys.path.append('/ufs/guido/lib/python')
# ```

# ## `dir` 函数
# 
# 内置函数 {func}`dir` 用于查找模块定义的名称。返回结果是经过排序的字符串列表：

# In[17]:


import fibo, sys

dir(fibo)


# 没有参数时，{func}`dir` 列出当前定义的名称：

# In[24]:


dir()[:10]


# ```{hint}
# 该函数列出所有类型的名称：变量、模块、函数等。
# ```
# 
# {func}`dir` 不会列出内置函数和变量的名称。这些内容的定义在标准模块 {mod}`builtins` 里：

# In[23]:


import builtins
dir(builtins)[:10]


# ## 包
# 
# 包是一种用“点式模块名”构造 Python 模块命名空间的方法。
# 
# 例如，模块名 `A.B` 表示包 `A` 中名为 `B` 的子模块。正如模块可以区分不同模块之间的全局变量名称一样，点式模块名可以区分 NumPy 或 Pillow 等不同多模块包之间的模块名称。
# 
# 假设要为统一处理声音文件与声音数据设计一个模块集（“包”）。声音文件的格式很多（通常以扩展名来识别，例如：`.wav`， `.aiff`， `.au`），因此，为了不同文件格式之间的转换，需要创建和维护一个不断增长的模块集合。为了实现对声音数据的不同处理（例如，混声、添加回声、均衡器功能、创造人工立体声效果），还要编写无穷无尽的模块流。下面这个分级文件树展示了这个包的架构：
# 
# ```python
# sound/                          Top-level package
#       __init__.py               Initialize the sound package
#       formats/                  Subpackage for file format conversions
#               __init__.py
#               wavread.py
#               wavwrite.py
#               aiffread.py
#               aiffwrite.py
#               auread.py
#               auwrite.py
#               ...
#       effects/                  Subpackage for sound effects
#               __init__.py
#               echo.py
#               surround.py
#               reverse.py
#               ...
#       filters/                  Subpackage for filters
#               __init__.py
#               equalizer.py
#               vocoder.py
#               karaoke.py
#               ...
# ```
# 
# 导入包时，Python 搜索 `sys.path` 里的目录，查找包的子目录。
# 
# Python 只把含 `__init__.py` 文件的目录当成包。这样可以防止以 `string` 等通用名称命名的目录，无意中屏蔽出现在后方模块搜索路径中的有效模块。 最简情况下，`__init__.py` 只是一个空文件，但该文件也可以执行包的初始化代码，或设置 `__all__` 变量，详见下文。
# 
# 还可以从包中导入单个模块，例如：
# 
# ```python
# import sound.effects.echo
# ```
# 
# 这段代码加载子模块 `sound.effects.echo`，但引用时必须使用子模块的全名：
# 
# ```python
# sound.effects.echo.echofilter(input, output, delay=0.7, atten=4)
# ```
# 
# 另一种导入子模块的方法是 ：
# 
# ```python
# from sound.effects import echo
# ```
# 
# 这段代码还可以加载子模块 `echo` ，不加包前缀也可以使用。因此，可以按如下方式使用：
# 
# ```python
# echo.echofilter(input, output, delay=0.7, atten=4)
# ```
# 
# Import 语句的另一种变体是直接导入所需的函数或变量：
# 
# ```python
# from sound.effects.echo import echofilter
# ```
# 
# 同样，这样也会加载子模块 `echo`，但可以直接使用函数 `echofilter()`：
# 
# ```python
# echofilter(input, output, delay=0.7, atten=4)
# ```
# 
# 注意，使用 `from package import item` 时，`item` 可以是包的子模块（或子包），也可以是包中定义的函数、类或变量等其他名称。`import` 语句首先测试包中是否定义了 `item`；如果未在包中定义，则假定 `item` 是模块，并尝试加载。如果找不到 `item`，则触发 {exc}`ImportError` 异常。
# 
# 相反，使用 `import item.subitem.subsubitem` 句法时，除最后一项外，每个 `item` 都必须是包；最后一项可以是模块或包，但不能是上一项中定义的类、函数或变量。

# 
