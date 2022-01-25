"""命令行解析库

简单使用步骤:

1. 导入 参数解析

2. 解析器 = 参数解析.〇参数解析器()

3. 解析器.添加参数()

4. 解析器.解析参数()
"""

导入 argparse
从 汉化通用 导入 _关键词参数中转英

匚其余 = argparse.REMAINDER
匚抑制 = argparse.SUPPRESS

_参数字典 = {
    '操作'    : 'action',
    '参数个数' : 'nargs',
    '常数'    : 'const',
    '默认值'  : 'default',
    '类型'    : 'type',
    '选择范围' : 'choices',
    '必需'    : 'required',
    '帮助'    : 'help',
    '用法名'  : 'metavar',
    '属性名'  : 'dest',
    '版本'   : 'version'
}
_操作值字典 = {
    '存储' : 'store',
    '存储常数' : 'store_const',
    '存储真' : 'store_true',
    '存储假' : 'store_false',
    '追加' : 'append',
    '追加常数' : 'append_const',
    '计数' : 'count',
    '帮助' : 'help',
    '版本' : 'version',
    '扩充' : 'extend'
}

类 〇文件类型(argparse.FileType):
    "创建文件对象类型的工厂"

    套路 __init__(分身, 模式='r', 缓冲区大小=1, 编码方式=空, 错误处理=空):
        分身._mode = 模式
        分身._bufsize = 缓冲区大小
        分身._encoding = 编码方式
        分身._errors = 错误处理

类 〇操作(argparse.Action):
    """操作对象可以传递给 *添加参数()* 的 *操作* 参数. 仅 *选项字符串列表*
    参数与 *添加参数()* 的关键词参数不同, 它是指应与此操作相关联的命令行
    选项字符串列表.
    """
    # def __init__(分身,
    #              选项字符串列表,
    #              属性名,
    #              参数个数=空,
    #              常数=空,
    #              默认值=空,
    #              类型=空,
    #              选择范围=空,
    #              必需=False,
    #              帮助=空,
    #              用法名=空):
    #     分身.option_strings = 选项字符串列表
    #     分身.dest = 属性名
    #     分身.nargs = 参数个数
    #     分身.const = 常数
    #     分身.default = 默认值
    #     分身.type = 类型
    #     分身.choices = 选择范围
    #     分身.required = 必需
    #     分身.help = 帮助
    #     分身.metavar = 用法名

    # def _get_kwargs(分身):
    #     names = [
    #         'option_strings',
    #         'dest',
    #         'nargs',
    #         'const',
    #         'default',
    #         'type',
    #         'choices',
    #         'help',
    #         'metavar',
    #     ]
    #     return [(name, getattr(分身, name)) for name in names]

    # def __call__(分身, 解析器, 名称空间, 值, 选项字符串=空):
    #     raise NotImplementedError('.__call__() 未定义')

〇帮助格式化 = argparse.HelpFormatter
〇原始描述_帮助格式化 = argparse.RawDescriptionHelpFormatter
〇原始文本_帮助格式化 = argparse.RawTextHelpFormatter
〇参数默认值_帮助格式化 = argparse.ArgumentDefaultsHelpFormatter
〇以类型为用法名_帮助格式化 = argparse.MetavarTypeHelpFormatter

类 〇参数解析器(argparse.ArgumentParser):
    """将命令行字符串解析为 Python 对象.

    关键词参数:
        程序 - 程序名称 (默认值: 系统.参数列表[0])

        用法 - 描述程序用法的字符串（默认值: 从解析器的参数生成)

        描述 - 显示在参数帮助信息之前的文本 (默认值: 空)

        结语 - 显示在参数帮助信息之前的文本 (默认值: 空)

        父对象 - 参数解析器对象列表, 其参数也应包括在内

        〇格式化 - 定制帮助信息输出的类

        前缀符 - 可选参数的前缀字符集 (默认值: '-')

        从文件_前缀符 - 文件的前缀字符集, 应从此类文件中读取更多参数 (默认值: 空)

        参数默认值 - 参数的全局默认值 (默认值: 空)

        冲突处理 - 解决相互冲突的可选参数的策略 (通常不必要)

        添加帮助 - 解析器增加 -h/--help 选项 (默认值: 真)

        允许缩写 - 当缩写参数模棱两可时, 允许长选项自动匹配缩写参数 (默认值: 真)
    """

    def __init__(分身,
                 程序=空,
                 用法=空,
                 描述=空,
                 结语=空,
                 父对象=[],
                 〇格式化=〇帮助格式化,
                 前缀符='-',
                 从文件_前缀符=空,
                 参数默认值=空,
                 冲突处理='报错',
                 添加帮助=真,
                 允许缩写=真):
        冲突处理字典 = {
            '报错' : 'error',
            '覆盖' : 'resolve'
        }
        super(〇参数解析器, 分身).__init__(
                 prog=程序,
                 usage=用法,
                 description=描述,
                 epilog=结语,
                 parents=父对象,
                 formatter_class=〇格式化,
                 prefix_chars=前缀符,
                 fromfile_prefix_chars=从文件_前缀符,
                 argument_default=参数默认值,
                 conflict_handler=冲突处理字典.获取(冲突处理, 冲突处理),
                 add_help=添加帮助,
                 allow_abbrev=允许缩写)

    套路 添加参数(分身, *名称或标志, **关键词参数):
        """参数说明如下:

        名称或标志 - 选项字符串的名字或者列表，例如 foo 或者 -f, --foo。

        操作 - 在命令行遇到该参数时采取的操作的基本类型。预置操作类型有:

            + '存储' : 存储参数的值, 这是默认操作
            + '存储常数' : 存储 *常数* 关键词参数指定的值
            + '存储真' : '存储常数' 的特殊情况, 用于存储 *真* 值
            + '存储假' : '存储常数' 的特殊情况, 用于存储 *假* 值
            + '追加' : 存储一个列表, 将每个参数值追加到列表中
            + '追加常数' : 存储一个列表, 将 *常数* 关键词参数指定的值追加到列表中
            + '计数' : 计数一个关键词参数出现的次数
            + '帮助' : 打印当前解析器中所有选项的完整帮助信息, 然后退出
            + '版本' : 要求有一个 *版本=* 关键词参数, 调用时打印版本信息并退出
            + '扩充' : 存储一个列表, 将每个参数值添加到列表中

        参数个数 - 应该读取的命令行参数数目。

        常数 - 某些 *操作* 和 *参数个数* 选择要求的常数值。

        默认值 - 命令行中没有出现该参数时的默认值。

        类型 - 命令行参数应该被转换成的类型。

        选择范围 - 参数允许值的容器。

        必需 - 该命令行选项是否可以省略（只针对可选参数）。

        帮助 - 参数的简短描述。

        用法名 - 参数在用法信息中的名字。

        属性名 - 给 *解析参数()* 返回的对象添加的属性名称。

        """
        关键词参数 = _关键词参数中转英(关键词参数, _参数字典, _操作值字典)
        返回 分身.add_argument(*名称或标志, **关键词参数)
    
    套路 添加子解析器(分身, **关键词参数) -> '_〇子解析器':
        """参数类似 *〇参数解析器* 的参数. 不同之处说明如下:

        标题 - 帮助信息中该子解析器组的标题

        解析器类 - 用于创建子解析器实例的类, 默认为当前参数解析器

        选项字符串 - 用于调用操作的选项字符串

        * 勿在中文编程中使用原 add_subparsers() 方法
        """
        子解析器字典 = {
            '标题' : 'title',
            '描述' : 'description',
            '程序' : 'prog',
            '解析器类' : 'parser_class',
            '操作' : 'action',
            '选项字符串' : 'option_string',
            '属性名' : 'dest',
            '必需' : 'required',
            '帮助' : 'help',
            '用法名' : 'metavar'
        }
        关键词参数 = _关键词参数中转英(关键词参数, 子解析器字典)
        返回 _〇子解析器(分身.add_subparsers(**关键词参数, parser_class=argparse.ArgumentParser))

    套路 解析参数(分身, 参数=空, 名称空间=空):
        返回 分身.parse_args(args=参数, namespace=名称空间)

    套路 解析已知参数(分身, 参数=空, 名称空间=空):
        返回 分身.parse_known_args(args=参数, namespace=名称空间)

    套路 添加参数组(分身, 标题=空, 描述=空) -> '_〇参数解析器':
        返回 _〇参数解析器(分身.add_argument_group(title=标题, description=描述))

    套路 添加互斥组(分身, 必需=假) -> '_〇参数解析器':
        返回 _〇参数解析器(分身.add_mutually_exclusive_group(required=必需))

    套路 设置默认值(分身, **关键词参数):
        分身.set_defaults(**关键词参数)

    套路 获取默认值(分身, 属性名):
        返回 分身.get_default(属性名)

    套路 打印用法(分身, 文件=空):
        分身.print_usage(文件)

    套路 打印帮助(分身, 文件=空):
        分身.print_help(文件)

    套路 格式用法(分身):
        返回 分身.format_usage()

    套路 格式帮助(分身):
        返回 分身.format_help()

    套路 参数行转为参数(分身, 参数行):
        返回 分身.convert_arg_line_to_args(参数行)

    套路 退出(分身, 状态=0, 消息=空):
        分身.exit(status=状态, message=消息)

    套路 错误(分身, 消息):
        分身.error(消息)

    套路 解析混杂参数(分身, 参数=空, 名称空间=空):
        返回 分身.parse_intermixed_args(args=参数, namespace=名称空间)

    套路 解析已知混杂参数(分身, 参数=空, 名称空间=空):
        返回 分身.parse_known_intermixed_args(args=参数, namespace=名称空间)


类 _〇参数解析器:

    套路 __init__(分身, 解析器对象):
        分身._解析器对象 = 解析器对象
        
    套路 添加参数(分身, *名称或标志, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, _参数字典, _操作值字典)
        返回 分身._解析器对象.add_argument(*名称或标志, **关键词参数)

    add_argument = 添加参数

    套路 设置默认值(分身, **关键词参数):
        分身._解析器对象.set_defaults(**关键词参数)

    set_defaults = 设置默认值

    套路 获取默认值(分身, 属性名):
        返回 分身._解析器对象.get_default(属性名)

    get_default = 获取默认值

    套路 添加参数组(分身, 标题=空, 描述=空) -> '_〇参数解析器':
        返回 _〇参数解析器(分身._解析器对象.add_argument_group(title=标题, description=描述))

    add_argument_group = 添加参数组

    套路 添加互斥组(分身, 必需=假) -> '_〇参数解析器':
        返回 _〇参数解析器(分身._解析器对象.add_mutually_exclusive_group(required=必需))

    add_mutually_exclusive_group = 添加互斥组


类 _〇子解析器:

    套路 __init__(分身, 子解析器对象):
        分身._子解析器对象 = 子解析器对象

    套路 添加解析器(分身, 名称, **关键词参数) -> '_〇参数解析器':
        """比参数解析器对象多了一个 *别名* 参数, 允许多个字符串表示同一个子解析器.
        例如在 svn 中, co 是 checkout 的别名, 所以 svn co == svn checkout
        """
        解析器参数字典 = {
            '程序' : 'prog',
            '用法' : 'usage',
            '描述' : 'description',
            '结语' : 'epilog',
            '父对象' : 'parents',
            '〇格式化' : 'formatter_class',
            '前缀符' : 'prefix_chars',
            '从文件_前缀符' : 'fromfile_prefix_chars',
            '参数默认值' : 'argument_default',
            '冲突处理' : 'conflict_handler',
            '添加帮助' : 'add_help',
            '允许缩写' : 'allow_abbrev',
            '别名' : 'aliases',
            '帮助' : 'help'
        }
        关键词参数 = _关键词参数中转英(关键词参数, 解析器参数字典)
        返回 _〇参数解析器(分身._子解析器对象.add_parser(名称, **关键词参数))

    add_parser = 添加解析器


