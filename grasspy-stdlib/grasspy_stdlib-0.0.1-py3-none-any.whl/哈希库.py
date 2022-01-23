"""哈希库模块 - 众多哈希函数通用接口.

new(name, data=b'', **kwargs) - 返回一个实现指定哈希函数的新哈希对象;
                                利用给定的二进制数据初始化哈希对象.

同时提供了以下命名构造函数, 使用这些函数比使用 new(name) 要更快:

md5(), sha1(), sha224(), sha256(), sha384(), sha512(), blake2b(), blake2s(),
sha3_224, sha3_256, sha3_384, sha3_512, shake_128, shake_256.

您的平台可能提供了其他算法, 但以上算法保证存在.
要知道可以将哪些算法名称传递给 new(), 请参见 '保证有算法' 和 '可用算法' 属性.

注意: adler32 或 crc32 哈希函数在 zlib 模块中.

请明智地选择哈希函数.  某些函数存在已知的碰撞弱点.
sha384 和 sha512 在 32 位平台上很慢.

哈希对象具有如下方法:
 - 更新(数据): 用数据中的字节更新哈希对象. 重复调用相当于
                 将所有参数连接起来的单次调用.
 - 摘要():     以字节对象返回当前已传递给 更新() 方法的数据摘要.
 - 十六进制摘要():  类似 摘要(), 不过返回的是两倍长度的字符串, 
                 仅包含十六进制数字.
 - 拷贝():       返回哈希对象的一个副本 (克隆). 
                 这可以用来高效计算共享相同初始子串的数据的摘要.

例如, 要获得字节串 'Nobody inspects the spammish repetition' 的摘要:

    >>> 导入 哈希库
    >>> m = 哈希库.md5()
    >>> m.更新(b"Nobody inspects")
    >>> m.更新(b" the spammish repetition")
    >>> m.摘要()
    b'\\xbbd\\x9c\\x83\\xdd\\x1e\\xa5\\xc9\\xd9\\xde\\xc9\\xa1\\x8d\\xf0\\xff\\xe9'

更紧凑的形式:

    >>> 哈希库.sha224(b"Nobody inspects the spammish repetition").十六进制摘要()
    'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2'

传入包含汉字的字符串时, 须将其编码为字节串, 例如: '为人民服务 向雷锋同志学习'.编码('utf-8)
"""

从 hashlib 导入 *

保证有算法 = algorithms_guaranteed
可用算法 = algorithms_available