"""
本模块用于访问解释器使用或维护的一些对象, 以及与解释器深度交互的一些函数.

动态对象:

argv|参数列表 -- 命令行参数; 参数列表[0] 为脚本路径名 (如果已知)\n
path|路径 -- 模块搜索路径; 路径[0] 为脚本目录, 否则为 ''\n
modules|模块々 -- 已加载模块的目录\n

displayhook|显示钩子 -- 用来在交互会话中显示结果\n
excepthook|异常钩子 -- 用来处理除 SystemExit 以外的任何未捕获异常\n
  要在交互会话中定制打印输出或安装自定义顶层异常处理程序, 
  请指定其他函数以替换这些对象.\n

stdin|标准输入 -- 标准输入文件对象; 由 输入() 使用\n
stdout|标准输出 -- 标准输出文件对象; 由 打印() 使用\n
stderr|错误输出 -- 标准错误对象; 用于错误消息\n
  通过指定其他文件对象 (或行为类似文件的对象),
  可以重定向解释器的所有输入输出 (I/O).\n

静态对象:

builtin_module_names|内置模块名单 -- 本解释器内置的模块名称元组\n
stdlib_module_names|标准库模块名单 -- 本解释器的标准库模块名称的冻结集合\n
copyright|版权 -- 与本解释器相关的版权声明\n
exec_prefix|解释器目录 -- 用于查找机器特定 Python 库的前缀 (目录)\n
executable|解释器路径 -- Python 解释器的可执行二进制文件的绝对路径\n
float_info|浮点型信息 -- 具名元组, 提供关于浮点数实现的信息\n
float_repr_style|浮点型表示样式 -- 表示浮点数的 表示() 输出样式的字符串\n
hash_info|哈希信息 -- 具名元组, 提供关于哈希算法的信息\n
hexversion|十六进制版本 -- 编码为单个整数的版本信息\n
implementation|实现信息 -- Python 实现信息\n
int_info|整型信息 -- 具名元组, 提供关于整数实现的信息\n
maxsize|最大大小 -- 最大支持的容器长度\n
maxunicode|最大统一码 -- 最大统一码码位值\n
platform|平台 -- 平台标识符\n
prefix|库目录 -- 用于查找 Python 库的前缀 (目录)\n
thread_info|线程信息 -- 具名元组, 提供关于线程实现的信息\n
version|版本 -- 以字符串表示的本解释器版本\n
version_info|版本信息 -- 以具名元组表示的版本信息\n

函数:

displayhook()|显示钩子() -- 打印一个对象到屏幕, 并将其保存到 builtins._\n
excepthook()|异常钩子() -- 打印一个异常及其回溯信息到 系统.错误输出\n
exc_info()|异常信息() -- 返回关于当前异常的线程安全信息\n
exit()|退出() -- 退出解释器并抛出 SystemExit\n
getprofile()|获取性能检测函数() -- 获取全局性能检测函数\n
getrefcount()|获取引用计数() -- 返回一个对象的引用计数 (加一 :-)\n
getrecursionlimit()|获取递归限值() -- 返回解释器的最大递归深度\n
getsizeof()|获取对象大小() -- 返回对象占用的字节数\n
gettrace()|获取追踪函数() -- 获取全局调试追踪函数\n
setdlopenflags() -- 设置要用于 dlopen() 调用的标志\n
setprofile()|设置性能检测函数() -- 设置全局性能检测函数\n
setrecursionlimit()|设置递归限值() -- 设置解释器的最大递归深度\n
settrace()|设置追踪函数 -- 设置全局调试追踪函数\n
"""

从 sys 导入 *

路径 = path   # 在 sysmodule.c 中的汉化 路径 不完整, 因为在随后的运行中 path 有所增加?
标准输入 = stdin
标准输出 = stdout
错误输出 = stderr

导入 sys

套路 标准输出重定向(文件对象):
    全局 标准输出
    标准输出 = sys.stdout = 文件对象

套路 错误输出重定向(文件对象):
    全局 错误输出
    错误输出 = sys.stderr = 文件对象
