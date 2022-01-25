'''本模块实现了一些特殊的容器，针对 Python 预置的容器数据类型，例如 列表、字典
和 元组，提供了另一种选择。

* 具名元组   创建具名元组子类的工厂函数
* 〇双端队列   类似列表(list)的容器，实现了在两端快速追加(append)和弹出(pop)
* 〇链式映射   类似字典(dict)的容器类，将多个映射集合到一个视图里面
* 〇计数器   字典的子类，用于计数可哈希对象
* 〇有序字典   字典的子类，保存了元素被添加的顺序
* 〇默认值字典   字典的子类，提供了一个工厂函数，为字典查询提供一个默认值
* 〇用户字典   封装的字典对象，简化了字典子类化
* 〇用户列表   封装的列表对象，简化了列表子类化
* 〇用户字符串 封装的字符串对象，简化了字符串子类化

'''

__all__ = ['〇双端队列', '〇默认值字典', '具名元组', '〇用户字典', '〇用户列表',
            '〇用户字符串', '〇计数器', '〇有序字典', '〇链式映射',
            'deque', 'defaultdict', 'namedtuple', 'UserDict', 'UserList',
            'UserString', 'Counter', 'OrderedDict', 'ChainMap']

从 collections 导入 *
from typing import NamedTuple
################################################################################
### 〇有序字典
################################################################################

类 〇有序字典(OrderedDict):
    '能记住插入顺序的字典'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as regular dictionaries.

    # The internal self.__map dict maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The sentinel is in self.__hardroot with a weakref proxy in self.__root.
    # The prev links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference in self.__map.
    # Those hard references disappear when a key is deleted from an OrderedDict.

    套路 __init__(分身, 其他=(), /, **关键词参数):
        '''初始化有序字典. 签名与常规字典相同. 保留关键词参数顺序.
        '''
        super().__init__(其他, **关键词参数)

    套路 清空(分身):
        '移除所有元素'
        分身.clear()

    套路 弹出项(分身, 最后=真):
        '''从字典中移除并返回一个 (键, 值) 对.

        如果 '最后' 为真, 则以后进先出的顺序弹出, 否则以先进先出的顺序弹出.
        '''
        如果 非 分身:
            报 键错误类('字典为空')
        返回 分身.popitem(最后)

    套路 移至端(分身, 键, 最后=真):
        '将现有元素移至末尾 (如果"最后"为假则是开头).'
        分身.move_to_end(键, 最后)

    更新 = OrderedDict.update

    套路 键々(分身):
        '返回一个集合类对象, 提供关于字典所有键的视图'
        返回 分身.keys()

    套路 项々(分身):
        '返回一个集合类对象, 提供关于字典所有项的视图'
        返回 分身.items()

    套路 值々(分身):
        '返回一个集合类对象, 提供关于字典所有值的视图'
        返回 分身.values()

    __marker = object()

    套路 弹出(分身, 键, 默认值=__marker):
        '''移除指定键并返回对应的值. 如果键未找到,
        有默认值则返回默认值, 无默认值则抛出键错误异常.
        '''
        if 键 in 分身:
            result = 分身[键]
            del 分身[键]
            return result
        if 默认值 is 分身.__marker:
            raise KeyError(键)
        return 默认值

    套路 设默认值(分身, 键, 默认值=空):
        '''如果 "键" 不在字典中, 则插入带默认值的键.
        如果 "键" 在字典中, 则返回对应的值, 否则返回默认值.
        '''
        返回 分身.setdefault(键, 默认值)

    套路 拷贝(分身):
        '返回有序字典的浅表拷贝'
        返回 分身.copy()

    @classmethod
    套路 从键创建(本类, 可迭代对象, 值=空) -> '〇有序字典':
        '''创建一个新的有序字典, 键来自可迭代对象, 值为给定的值'''
        返回 本类.fromkeys(可迭代对象, 值)
    

################################################################################
### 具名元组
################################################################################

套路 具名元组(类型名称, 字段名称, *, 重命名=假, 默认值=空, 模块=空) -> NamedTuple:
    """生成可以用名称来访问元素内容的元组子类.

    >>> 点 = 具名元组('点', ['x', 'y'])
    >>> 点.__文档__                   # 新类的文档
    '点(x, y)'
    >>> p = 点(11, y=22)             # 用未知参数或关键词实例化
    >>> p[0] + p[1]                     # 像普通元组一样索引
    33
    >>> x, y = p                        # 像常规元组一样解包
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # 字段也可以通过名称来访问
    33
    >>> d = p._转字典()                 # 转换为字典
    >>> d['x']
    11
    >>> 点(**d)                      # 从字典得到参数
    点(x=11, y=22)
    >>> p._替换(x=100)               # _替换() 类似 串.替换(), 但针对的是具名字段
    点(x=100, y=22)
    """
    结果 = namedtuple(类型名称, 字段名称, rename=重命名, defaults=默认值, module=模块)
    结果._字段 = 结果._fields
    结果._字段默认值 = 结果._fields_defaults
    结果._生成 = 结果._make
    结果._替换 = 结果._replace
    结果._转字典 = 结果._asdict
    返回 结果


################################################################################
### 〇计数器
################################################################################

类 〇计数器(Counter):
    """字典子类, 用于统计元素的出现次数.
    
    >>> c = 〇计数器('abcdeabcdabcaba')  # 计数字符串中的元素

    >>> c.最常见(3)                # 三个最常见的元素
    [('a', 5), ('b', 4), ('c', 3)]
    >>> 排序(c)                       # 列出所有元素, 同一元素仅列一个
    ['a', 'b', 'c', 'd', 'e']
    >>> ''.连接(排序(c.所有元素()))   # 列出所有元素, 同一元素有几个列几个
    'aaaaabbbbcccdde'
    >>> 和(c.值())                 # 所有计数的总和
    15

    >>> c['a']                          # 字母 'a' 的出现次数
    5
    >>> 取 元素 于 'shazam':           # 从一个可迭代对象更新计数
    ...     c[元素] += 1                # 每个元素的计数加 1
    >>> c['a']                          # 现在有七个 'a'
    7
    >>> 删 c['b']                      # 删除所有 'b'
    >>> c['b']                          # 现在有零个 'b'
    0

    >>> d = 〇计数器('simsalabim')       # 再创建一个计数器
    >>> c.更新(d)                     # 加上第二个计数器
    >>> c['a']                          # 现在有九个 'a'
    9

    >>> c.清空()                       # 清空计数器
    >>> c
    Counter()

    注意:  如果一个计数设为 0 或减至 0, 它仍会留在计数器中,zero, it will remain
    直到该项被删除或计数器被清空:

    >>> c = 〇计数器('aaabbc')
    >>> c['b'] -= 2                     # 'b' 的计数减 2
    >>> c.最常见()                 # 'b' 仍在, 但其计数为 0
    [('a', 3), ('c', 1), ('b', 0)]
    """

    套路 最常见(分身, n=空):
        '''列出出现次数最多的 n 个元素及其相应的次数.
        如果 n 为空, 则列出所有元素及其出现次数.
        ''' 
        返回 分身.most_common(n)

    套路 所有元素(分身):
        '返回一个迭代器, 每个元素按其出现次数重复.'
        返回 分身.elements()

    套路 更新(分身, 可迭代对象=空, /, **关键词参数):
        '类似字典的更新方法, 但次数是增加而非替换.'
        分身.update(可迭代对象, **关键词参数)

    套路 减去(分身, 可迭代对象=空, /, **关键词参数):
        '类似字典的更新方法, 但次数是减少而非替换. 次数可以为 0 或负数.'
        分身.subtract(可迭代对象, **关键词参数)

    套路 拷贝(分身):
        '返回一个浅表拷贝'
        返回 分身.copy()

    @classmethod
    def 从键创建(cls, 可迭代对象, 值=空):
        raise NotImplementedError(
            '〇计数器.从键创建() 未定义. 请改用 〇计数器(可迭代对象).')


########################################################################
###  〇链式映射
########################################################################

类 〇链式映射(ChainMap):
    '''将多个字典 (或其他映射) 组织在一起, 产生单个可更新的视图.

    各映射存储在一个列表中. 使用 所有映射 属性可以访问或更新列表.

    查找操作会依次搜索各映射, 直至找到所需的键. 写入/更新/删除操作
    则相反, 仅针对第一个映射进行.
    '''
    套路 __init__(分身, *映射):
        分身.所有映射 = 分身.maps = 列表(映射) or [{}]

    套路 获取(分身, 键, 默认值=空):
        返回 分身.get(键, 默认值)

    @classmethod
    套路 从键创建(本类, 可迭代对象, *参数) -> '〇链式映射':
        '利用从可迭代对象创建的单个字典创建一个链式映射'
        返回 本类(dict.fromkeys(可迭代对象, *参数))

    套路 拷贝(分身) -> '〇链式映射':
        "用 所有映射[0] 的一个新副本和对 所有映射[1:] 的引用新建一个链式映射"
        返回 分身.copy()

    套路 新建_子映射(分身, 映射=空) -> '〇链式映射':
        '''返回一个新的链式映射: 新映射在前, 先前的所有映射在后.
        如果未提供映射, 则使用空字典.
        '''
        返回 分身.new_child(映射)

    @属性
    套路 所有父映射(分身) -> '〇链式映射':
        '返回一个由 *所有映射[1:]* 构成的新链式映射'
        返回 分身.parents

    套路 弹出项(分身):
        '从 *所有映射[0]* 移除并返回一个元素对'
        返回 分身.popitem()

    套路 弹出(分身, 键, *参数):
        '从 *所有映射[0]* 移除指定键并返回其值'
        返回 分身.pop(键, *参数)

    套路 清空(分身):
        '清空 *所有映射[0]*, 其余映射保持不变'
        分身.clear()


################################################################################
### 〇用户字典
################################################################################

类 〇用户字典(UserDict):

    套路 __init__(分身, 字典=空, /, **关键词参数):
        super().__init__(字典, **关键词参数)
        分身.数据 = 分身.data

    套路 拷贝(分身):
        返回 分身.copy()

    @类方法
    套路 从键创建(本类, 可迭代对象, 值=空):
        d = 本类()
        for key in 可迭代对象:
            d[key] = 值
        返回 d

    
################################################################################
### 〇用户列表
################################################################################

类 〇用户列表(UserList):
    """堪称完整的用户自定义列表对象包装器"""
    def __init__(self, 初始列表=空):
        super().__init__(初始列表)
        self.数据 = self.data
        
    def 追加(self, 元素): self.data.append(元素)
    def 插入(self, i, 元素): self.data.insert(i, 元素)
    def 弹出(self, i=-1): return self.data.pop(i)
    def 移除(self, 元素): self.data.remove(元素)
    def 清空(self): self.data.clear()
    def 拷贝(self): return self.__class__(self)
    def 计数(self, 元素): return self.data.count(元素)
    def 索引(self, 元素, *参数): return self.data.index(元素, *参数)
    def 反转(self): self.data.reverse()
    def 排序(self, /, *参数, **关键词参数): self.data.sort(*参数, **关键词参数)
    def 扩充(self, 其他):
        if isinstance(其他, UserList):
            self.data.extend(其他.data)
        else:
            self.data.extend(其他)


################################################################################
### 〇用户字符串
################################################################################
导入 sys 为 _sys
类 〇用户字符串(UserString):

    def __init__(self, 序列):
        super().__init__(序列)
        self.数据 = self.data

    def 首字母大写(self): return self.__class__(self.data.capitalize())
    def 强力小写(self):
        return self.__class__(self.data.casefold())
    def 居中(self, 宽度, *参数):
        return self.__class__(self.data.center(宽度, *参数))
    def 计数(self, 子串, 起=0, 止=_sys.maxsize):
        if isinstance(子串, UserString):
            子串 = 子串.data
        return self.data.count(子串, 起, 止)
    def 编码(self, 编码方式='utf-8', 错误处理='严格'):
        编码方式 = 'utf-8' if 编码方式 is None else 编码方式
        错误处理 = 'strict' if 错误处理 is None else 错误处理
        return self.data.encode(编码方式, 错误处理)
    def 结尾是(self, 后缀, 起=0, 止=_sys.maxsize):
        return self.data.endswith(后缀, 起, 止)
    def 展开tab(self, tab大小=8):
        return self.__class__(self.data.expandtabs(tab大小))
    def 查找(self, 子串, 起=0, 止=_sys.maxsize):
        if isinstance(子串, UserString):
            子串 = 子串.data
        return self.data.find(子串, 起, 止)
    def 格式化(self, /, *args, **kwds):
        return self.data.format(*args, **kwds)
    def 格式化_映射(self, 映射):
        return self.data.format_map(映射)
    def 索引(self, 子串, 起=0, 止=_sys.maxsize):
        return self.data.index(子串, 起, 止)
    def 是文字(self): return self.data.isalpha()
    def 是文字数字(self): return self.data.isalnum()
    def 是ascii(self): return self.data.isascii()
    def 是十进制串(self): return self.data.isdecimal()
    def 是数码(self): return self.data.isdigit()
    def 是标识符(self): return self.data.isidentifier()
    def 是小写(self): return self.data.islower()
    def 是数字(self): return self.data.isnumeric()
    def 是可打印串(self): return self.data.isprintable()
    def 是空白(self): return self.data.isspace()
    def 是标题(self): return self.data.istitle()
    def 是大写(self): return self.data.isupper()
    def 连接(self, seq): return self.data.join(seq)
    def 左对齐(self, 宽度, *参数):
        return self.__class__(self.data.ljust(宽度, *参数))
    def 小写(self): return self.__class__(self.data.lower())
    def 左修剪(self, 字符々=None): return self.__class__(self.data.lstrip(字符々))
    制转换表 = maketrans = str.maketrans
    def 划分(self, 分隔符):
        return self.data.partition(分隔符)
    def 替换(self, 旧, 新, 次数=-1):
        if isinstance(旧, UserString):
            旧 = 旧.data
        if isinstance(新, UserString):
            新 = 新.data
        return self.__class__(self.data.replace(旧, 新, 次数))
    def 右查找(self, 子串, 起=0, 止=_sys.maxsize):
        if isinstance(子串, UserString):
            子串 = 子串.data
        return self.data.rfind(子串, 起, 止)
    def 右索引(self, 子串, 起=0, 止=_sys.maxsize):
        return self.data.rindex(子串, 起, 止)
    def 右对齐(self, 宽度, *参数):
        return self.__class__(self.data.rjust(宽度, *参数))
    def 右划分(self, 分隔符):
        return self.data.rpartition(分隔符)
    def 右修剪(self, 字符々=None):
        return self.__class__(self.data.rstrip(字符々))
    def 分割(self, 分隔符=None, 最大分割次数=-1):
        return self.data.split(分隔符, 最大分割次数)
    def 右分割(self, 分隔符=None, 最大分割次数=-1):
        return self.data.rsplit(分隔符, 最大分割次数)
    def 分行(self, 保留换行符=假): return self.data.splitlines(保留换行符)
    def 开头是(self, 前缀, 起=0, 止=_sys.maxsize):
        return self.data.startswith(前缀, 起, 止)
    def 修剪(self, 字符々=空): return self.__class__(self.data.strip(字符々))
    def 大小写互换(self): return self.__class__(self.data.swapcase())
    def 标题(self): return self.__class__(self.data.title())
    def 转换(self, *参数):
        return self.__class__(self.data.translate(*参数))
    def 大写(self): return self.__class__(self.data.upper())
    def 填零(self, 宽度): return self.__class__(self.data.zfill(宽度))


类 〇双端队列(deque):
    '''最大的好处就是实现了从队列头部快速增加和取出对象: 左弹出(), 左追加(),
    时间复杂度是 O(1)。列表也能支持从头部添加和取出对象, 但时间复杂度是 O(n).
    '''     

类 〇默认值字典(defaultdict):
    """使用原生数据结构'字典'的时候，如果用 d[键] 这样的方式访问，当指定的'键'不存在时，
    会抛出'键错误'异常。但如果使用'默认值字典'，只要你传入一个默认值工厂方法，
    那么请求一个不存在的'键'时，便会调用这个工厂方法, 使用其结果来作为这个'键'的默认值。
    """
    