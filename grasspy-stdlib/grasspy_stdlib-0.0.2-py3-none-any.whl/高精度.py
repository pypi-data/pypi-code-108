"""支持精确十进制浮点数计算 - decimal (仅汉化了一点点)

float - 单精度, double - 双精度, decimal - 高精度

>>> 从 高精度 导入 *
>>> 设置上下文(〇扩展上下文)
>>> 〇高精度(0)
〇高精度('0')
>>> 〇高精度('1')
〇高精度('1')
>>> 〇高精度('-.0123')
〇高精度('-0.0123')
>>> 〇高精度(123456)
〇高精度('123456')
>>> 〇高精度('123.45e12345678')
〇高精度('1.2345E+12345680')
>>> 〇高精度('1.33') + 〇高精度('1.27')
〇高精度('2.60')
>>> 〇高精度('12.34') + 〇高精度('3.87') - 〇高精度('18.41')
〇高精度('-2.20')
>>> 数 = 〇高精度(1)
>>> 打印(数 / 〇高精度(3))
0.333333333
>>> 获取上下文().prec = 18
>>> 打印(数 / 〇高精度(3))
0.333333333333333333
>>> 打印(数.开方())
1
>>> 打印(〇高精度(3).开方())
1.73205080756887729
>>> 打印(〇高精度(3) ** 123)
4.85192780976896427E+58
>>> 无穷 = 〇高精度(1) / 〇高精度(0)
>>> 打印(无穷)
Infinity
>>> 负无穷 = 〇高精度(-1) / 〇高精度(0)
>>> 打印(负无穷)
-Infinity
>>> 打印(负无穷 + 无穷)
NaN
>>> 打印(负无穷 * 无穷)
-Infinity
>>> 打印(数 / 0)
Infinity
>>> getcontext().traps[DivisionByZero] = 1
>>> 打印(数 / 0)
Traceback (most recent call last):
  ...
  ...
  ...
decimal.DivisionByZero: x / 0
>>> c = Context()
>>> c.traps[InvalidOperation] = 0
>>> 打印(c.flags[InvalidOperation])
0
>>> c.divide(〇高精度(0), 〇高精度(0))
〇高精度('NaN')
>>> c.traps[InvalidOperation] = 1
>>> 打印(c.flags[InvalidOperation])
1
>>> c.flags[InvalidOperation] = 0
>>> 打印(c.flags[InvalidOperation])
0
>>> 打印(c.divide(〇高精度(0), 〇高精度(0)))
Traceback (most recent call last):
  ...
  ...
  ...
decimal.InvalidOperation: 0 / 0
>>> 打印(c.flags[InvalidOperation])
1
>>> c.flags[InvalidOperation] = 0
>>> c.traps[InvalidOperation] = 0
>>> 打印(c.divide(〇高精度(0), 〇高精度(0)))
NaN
>>> 打印(c.flags[InvalidOperation])
1
>>>
"""

__all__ = [
    # Two major classes
    'Decimal', 'Context',
    '〇高精度', '〇上下文',

    # Named tuple representation
    'DecimalTuple',
    # '〇高精度元组',

    # Contexts
    'DefaultContext', 'BasicContext', 'ExtendedContext',
    '〇默认上下文', '〇基本上下文', '〇扩展上下文',

    # Exceptions
    'DecimalException', 'Clamped', 'InvalidOperation', 'DivisionByZero',
    'Inexact', 'Rounded', 'Subnormal', 'Overflow', 'Underflow',
    'FloatOperation',

    # Exceptional conditions that trigger InvalidOperation
    'DivisionImpossible', 'InvalidContext', 'ConversionSyntax', 'DivisionUndefined',

    # Constants for use in setting up contexts
    'ROUND_DOWN', 'ROUND_HALF_UP', 'ROUND_HALF_EVEN', 'ROUND_CEILING',
    'ROUND_FLOOR', 'ROUND_UP', 'ROUND_HALF_DOWN', 'ROUND_05UP',

    # Functions for manipulating contexts
    'setcontext', 'getcontext', 'localcontext',
    '设置上下文', '获取上下文', '本地上下文',

    # Limits for the C version for compatibility
    'MAX_PREC',  'MAX_EMAX', 'MIN_EMIN', 'MIN_ETINY',

    # C version: compile time choice that enables the thread local context (deprecated, now always true)
    'HAVE_THREADS',

    # C version: compile time choice that enables the coroutine local context
    'HAVE_CONTEXTVAR'
]

从 decimal 导入 *

类 〇高精度(Decimal):
    """高精度小数类

    >>> 〇高精度('3.14')              # 字符串
    〇高精度('3.14')
    >>> 〇高精度((0, (3, 1, 4), -2))  # 元组 (符号, 数字元组, 指数)
    〇高精度('3.14')
    >>> 〇高精度(314)                 # 整数
    〇高精度('314')
    >>> 〇高精度(〇高精度(314))        # 另一个高精度数实例
    〇高精度('314')
    >>> 〇高精度('  3.14  \\n')        # 首尾可以有空白字符
    〇高精度('3.14')
    """

    def __repr__(self):
        """将数字表示为 〇高精度 的一个对象."""
        # Invariant:  eval(repr(d)) == d
        return "〇高精度('%s')" % str(self)

    @classmethod
    def 从浮点数(cls, f):
        """将一个浮点数如实转换为高精度小数

        Note that Decimal.from_float(0.1) is not the same as Decimal('0.1').
        Since 0.1 is not exactly representable in binary floating point, the
        value is stored as the nearest representable value which is
        0x1.999999999999ap-4.  The exact equivalent of the value in decimal
        is 0.1000000000000000055511151231257827021181583404541015625.

        >>> 〇高精度.从浮点数(0.1)
        〇高精度('0.1000000000000000055511151231257827021181583404541015625')
        >>> 〇高精度.从浮点数(浮点型('nan'))
        〇高精度('NaN')
        >>> 〇高精度.从浮点数(浮点型('inf'))
        〇高精度('Infinity')
        >>> 〇高精度.从浮点数(-浮点型('inf'))
        〇高精度('-Infinity')
        >>> 〇高精度.从浮点数(-0.0)
        〇高精度('-0')

        """
        返回 cls.from_float(f)

    def 量化(self, 指数, 四舍五入=None, 上下文=None):
        """Quantize self so its exponent is the same as that of exp.

        Similar to self._rescale(exp._exp) but with error checking.
        """
        返回 self.quantize(指数, rounding=四舍五入, context=上下文)

    def 比较(self, 其他, 上下文=空):
        返回 self.compare(其他, context=上下文)

    def 开方(self, 上下文=空):
        返回 self.sqrt(context=上下文)


类 〇上下文(Context):
    def __init__(self, 精度=None, rounding=None, Emin=None, Emax=None,
                       capitals=None, clamp=None, 标志々=None, 陷阱々=None,
                       _ignored_flags=None):
        super().__init__(prec=精度, rounding=None, Emin=None, Emax=None,
                       capitals=None, clamp=None, flags=标志々, traps=陷阱々,
                       _ignored_flags=None)
        self.精度 = self.prec
        self.标志々 = self.flags
        self.陷阱々 = self.traps


套路 获取上下文():
    返回 getcontext()

套路 设置上下文(上下文):
    setcontext(上下文)

套路 本地上下文(上下文=None):
    返回 localcontext(上下文)

〇默认上下文 = DefaultContext
〇基本上下文 = BasicContext
〇扩展上下文 = ExtendedContext