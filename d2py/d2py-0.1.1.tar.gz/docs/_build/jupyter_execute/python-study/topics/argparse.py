#!/usr/bin/env python
# coding: utf-8

# # `argparse`
# 
# {mod}`argparse`：命令行选项、参数和子命令解析器
# 
# ## `ArgumentParser` 对象
# 
# ```python
# class argparse.ArgumentParser(prog=None,
#                               usage=None,
#                               description=None,
#                               epilog=None,
#                               parents=[],
#                               formatter_class=argparse.HelpFormatter,
#                               prefix_chars='-',
#                               fromfile_prefix_chars=None,
#                               argument_default=None,
#                               conflict_handler='error',
#                               add_help=True,
#                               allow_abbrev=True,
#                               exit_on_error=True)
# 
# ```
# 
# 创建一个新的 {class}`ArgumentParser` 对象。所有的参数都应当作为关键字参数传入。
# 
# - {command}`prog`：程序的名称（默认值：`os.path.basename(sys.argv[0])`）
# - {command}`usage`：描述程序用途的字符串（默认值：从添加到解析器的参数生成）
# - {command}`description`：在参数帮助文档之前显示的文本（默认值：`None`）
# - {command}`epilog`：在参数帮助文档之后显示的文本（默认值： `None`）
# - {command}`parents`：{class}`ArgumentParser` 对象的列表，它们的参数也应包含在内
# - {command}`formatter_class`：用于自定义帮助文档输出格式的类
# - {command}`prefix_chars`：可选参数的前缀字符集合（默认值： `'-'`）
# - {command}`fromfile_prefix_chars`：当需要从文件中读取其他参数时，用于标识文件名的前缀字符集合（默认值： `None`）
# - {command}`argument_default`：参数的全局默认值（默认值： `None`）
# - {command}`conflict_handler`：解决冲突选项的策略（通常是不必要的）
# - {command}`add_help`：为解析器添加一个 {command}`-h/--help` 选项（默认值： `True`）
# - {command}`allow_abbrev`：如果缩写是无歧义的，则允许缩写长选项 （默认值：`True`）
# - {command}`exit_on_error`：决定当错误发生时是否让 {class}`ArgumentParser` 附带错误信息退出。（默认值: `True`）

# In[ ]:




