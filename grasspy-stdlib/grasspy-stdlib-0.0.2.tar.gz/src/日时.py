"""本模块提供用于处理日期时间的类: 
〇日期, 〇时间, 〇日时, 〇时间差, 〇时区信息, 〇时区"""

# 时区相关部分有待进一步汉化和仔细测试

导入 datetime
从 时间 导入 时间元组汉化

最小年份 = 1
最大年份 = 9999

_月名称 = [None, "1 月", "2 月", "3 月", "4 月", "5 月", "6 月",
                     "7 月", "8 月", "9 月", "10 月", "11 月", "12 月"]
_日名称 = [None, "周一", "周二", "周三", "周四", "周五", "周六", "周日"]

_时间规格字典 = {
    '自动'   : 'auto',
    '小时数' : 'hours',
    '分钟数' : 'minutes',
    '秒数'   : 'seconds',
    '毫秒数' : 'milliseconds',
    '微秒数' : 'microseconds'
}

def _divide_and_round(a, b):
    """divide a by b and round result to the nearest integer

    When the ratio is exactly half-way between two integers,
    the even integer is returned.
    """
    # Based on the reference implementation for divmod_near
    # in Objects/longobject.c.
    q, r = divmod(a, b)
    # round up if either r / b > 0.5, or r / b == 0.5 and q is odd.
    # The expression r / b > 0.5 is equivalent to 2 * r > b if b is
    # positive, 2 * r < b if b negative.
    r *= 2
    greater_than_half = r > b if b > 0 else r < b
    if greater_than_half or r == b and q % 2 == 1:
        q += 1

    return q

类 〇时间差(datetime.timedelta):
    """代表两个日期时间对象之差.

    时间差 = 〇时间差(天数=0, 秒数=0, 微秒数=0, 毫秒数=0, 分钟数=0, 小时数=0, 周数=0)

    所有参数都是可选参数, 可以为正/负整数或浮点数, 默认值为 0.

    支持的运算符:

    - 加/减一个时间差对象
    - 单目加/减/绝对值
    - 与另一个时间差对象比较
    - 乘/除一个整数

    此外, 两个日期时间对象相减得到一个时间差对象,
    日期时间对象加/减一个时间差得到一个日期时间对象.
    """

    套路 __new__(本类, 天数=0, 秒数=0, 微秒数=0, 毫秒数=0, 分钟数=0, 小时数=0, 周数=0):
        返回 super().__new__(本类, days=天数, seconds=秒数, microseconds=微秒数,
                milliseconds=毫秒数, minutes=分钟数, hours=小时数, weeks=周数)

    def __repr__(self):
        args = []
        if self.days:
            args.append("天数=%d" % self.days)
        if self.seconds:
            args.append("秒数=%d" % self.seconds)
        if self.microseconds:
            args.append("微秒数=%d" % self.microseconds)
        if not args:
            args.append('0')
        return "%s.%s(%s)" % ('日时',
                              '〇时间差',
                              ', '.join(args))

    def __str__(self):
        mm, ss = divmod(self.seconds, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d:%02d" % (hh, mm, ss)
        if self.days:
            s = ("%d 天, " % self.days) + s
        if self.microseconds:
            s = s + ".%06d" % self.microseconds
        return s

    套路 总秒数(分身):
        "该期间内的总秒数"
        返回 分身.total_seconds()

    @属性
    套路 天数(分身):
        返回 分身.days
    
    @属性
    套路 秒数(分身):
        ">= 0 且小于 1 天"
        返回 分身.seconds

    @属性
    套路 微秒数(分身):
        ">= 0 且小于 1 秒"
        返回 分身.microseconds

    def __add__(self, other):
        if isinstance(other, datetime.timedelta):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            return 〇时间差(self.days + other.days,
                             self.seconds + other.seconds,
                             self.microseconds + other.microseconds)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, datetime.timedelta):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            return 〇时间差(self.days - other.days,
                             self.seconds - other.seconds,
                             self.microseconds - other.microseconds)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, datetime.timedelta):
            return -self + other
        return NotImplemented

    def __neg__(self):
        # for CPython compatibility, we cannot use
        # our __class__ here, but need a real timedelta
        return 〇时间差(-self.days,
                         -self.seconds,
                         -self.microseconds)

    def __pos__(self):
        return self

    def __abs__(self):
        if self.days < 0:
            return -self
        else:
            return self

    def __mul__(self, other):
        if isinstance(other, int):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            return 〇时间差(self.days * other,
                             self.seconds * other,
                             self.microseconds * other)
        if isinstance(other, float):
            usec = self._to_microseconds()
            a, b = other.as_integer_ratio()
            return 〇时间差(0, 0, _divide_and_round(usec * a, b))
        return NotImplemented

    __rmul__ = __mul__

    def _to_microseconds(self):
        return ((self.days * (24*3600) + self.seconds) * 1000000 +
                self.microseconds)

    def __floordiv__(self, other):
        if not isinstance(other, (int, datetime.timedelta)):
            return NotImplemented
        usec = self._to_microseconds()
        if isinstance(other, datetime.timedelta):
            return usec // other._to_microseconds()
        if isinstance(other, int):
            return 〇时间差(0, 0, usec // other)

    def __truediv__(self, other):
        if not isinstance(other, (int, float, datetime.timedelta)):
            return NotImplemented
        usec = self._to_microseconds()
        if isinstance(other, datetime.timedelta):
            return usec / other._to_microseconds()
        if isinstance(other, int):
            return 〇时间差(0, 0, _divide_and_round(usec, other))
        if isinstance(other, float):
            a, b = other.as_integer_ratio()
            return 〇时间差(0, 0, _divide_and_round(b * usec, a))

    def __mod__(self, other):
        if isinstance(other, datetime.timedelta):
            r = self._to_microseconds() % other._to_microseconds()
            return 〇时间差(0, 0, r)
        return NotImplemented

    def __divmod__(self, other):
        if isinstance(other, datetime.timedelta):
            q, r = divmod(self._to_microseconds(),
                          other._to_microseconds())
            return q, 〇时间差(0, 0, r)
        return NotImplemented

〇时间差.最小值 = datetime.timedelta.min
〇时间差.最大值 = datetime.timedelta.max
〇时间差.分辨率 = datetime.timedelta.resolution


类 〇日期(datetime.date):
    """〇日期(年, 月, 日) --> 日期对象
    
    其他构造函数 (类方法):
    
    从时间戳()
    今日()
    从序数()
    从iso格式()
    从iso日历()

    方法:

    时间元组()
    转序数()
    周之日()
    iso周之日(), iso日历(), iso格式()
    转字符串()
    转格式串()

    属性 (只读):
    年, 月, 日
    """

    套路 __new__(本类, 年, 月, 日):
        返回 super().__new__(本类, 年, 月, 日)

    @classmethod
    套路 从时间戳(本类, 时间) -> '〇日期':
        "从 时间.时间() 之类的时间戳构造一个日期对象"
        返回 本类.fromtimestamp(时间)

    @classmethod
    套路 今日(本类) -> '〇日期':
        "从 时间.时间() 构造一个日期对象"
        返回 本类.today()

    @classmethod
    套路 从序数(本类, n) -> '〇日期':
        "n - 第 n 天. 1 年的 1 月 1 日为第 1 天."
        返回 本类.fromordinal(n)

    @classmethod
    套路 从iso格式(本类, 日期字符串) -> '〇日期':
        "从 〇日期.iso格式() 的输出构造一个日期对象."
        返回 本类.fromisoformat(日期字符串)

    @classmethod
    套路 从iso日历(本类, 年, 第几周, 周之日) -> '〇日期':
        "从 iso 年/周数/周之日 构造一个日期对象. 日期.iso日历() 函数的反函数"
        返回 本类.fromisocalendar(年, 第几周, 周之日)

    套路 转字符串(分身):
        "返回一个表示日期的字符串"
        weekday = 分身.toordinal() % 7 or 7
        return "%s %04d 年 %s %d 日 00:00:00" % (
            _日名称[weekday],
            分身.year, 
            _月名称[分身.month],
            分身.day)

    套路 转格式串(分身, 格式):
        返回 分身.strftime(格式)

    套路 iso格式(分身):
        "返回 iso 格式的日期, 即 YYYY-MM-DD"
        返回 分身.isoformat()

    @property
    套路 年(分身):
        返回 分身.year
    
    @property
    套路 月(分身):
        返回 分身.month

    @property
    套路 日(分身):
        返回 分身.day

    套路 时间元组(分身):
        "返回与 时间.本地时元组() 兼容的本地时间元组"
        返回 时间元组汉化(分身.timetuple())

    套路 转序数(分身):
        "该日期对象为第几天. 1 年的 1 月 1 日为第 1 天"
        返回 分身.toordinal()

    套路 替换(分身, 年=空, 月=空, 日=空) -> '〇日期':
        "使用给定的新值返回一个新的日期对象"
        if 年 is None:
            年 = 分身.year
        if 月 is None:
            月 = 分身.month
        if 日 is None:
            日 = 分身.day
        return type(分身)(年, 月, 日)

    def __sub__(self, other):
        """Subtract two dates, or a date and a timedelta."""
        if isinstance(other, datetime.timedelta):
            return self + datetime.timedelta(-other.days)
        if isinstance(other, datetime.date):
            days1 = self.toordinal()
            days2 = other.toordinal()
            return 〇时间差(days1 - days2)
        return NotImplemented

    套路 周之日(分身):
        "周一 == 0 ... 周日 == 6"
        返回 分身.weekday()

    套路 iso周之日(分身):
        "周一 == 1 ... 周日 == 7"
        返回 分身.isoweekday()

    套路 iso日历(分身):
        "返回一个 3 元组: (年, 第几周, 周之日)"
        返回 分身.isocalendar()

〇日期.最小值 = 〇日期(1, 1, 1)
〇日期.最大值 = 〇日期(9999, 12, 31)
〇日期.分辨率 = 〇时间差(天数=1)


类 〇时区信息(datetime.tzinfo):

    套路 从utc(分身, 日期时间):
        "UTC 日期时间 -> 本地日期时间"
        返回 分身.fromutc(日期时间)

类 〇时间(datetime.time):
    """〇时间([时[, 分[, 秒[, 微秒[, 时区信息]]]]]) --> 时间对象

    方法:

    转格式串()
    iso格式()
    utc偏移量()
    时区名称()
    夏令时()

    属性 (只读):
    时, 分, 秒, 微秒, 时区信息, 折叠
    """

    套路 __new__(本类, 时=0, 分=0, 秒=0, 微秒=0, 时区信息=空, *, 折叠=0):
        返回 super().__new__(本类, hour=时, minute=分, second=秒,
                            microsecond=微秒, tzinfo=时区信息, fold=折叠)

    @property
    套路 时(分身):
        返回 分身.hour

    @property
    套路 分(分身):
        返回 分身.minute

    @property
    套路 秒(分身):
        返回 分身.second

    @property
    套路 微秒(分身):
        返回 分身.microsecond

    @property
    套路 时区信息(分身):
        返回 分身.tzinfo

    @property
    套路 折叠(分身):
        返回 分身.fold

    套路 iso格式(分身, 时间规格='自动'):
        '''时间规格选项: 自动, 小时数, 分钟数, 秒数, 毫秒数, 微秒数'''
        时间规格 = _时间规格字典.获取(时间规格, 时间规格)
        返回 分身.isoformat(时间规格)

    @classmethod
    套路 从iso格式(本类, 时间字符串) -> '〇时间':
        "从 iso格式() 的输出构建一个时间对象"
        返回 本类.fromisoformat(时间字符串)

    套路 转格式串(分身, 格式):
        返回 分身.strftime(格式)

    套路 utc偏移量(分身):
        "将时区偏移量作为时间差对象返回"
        返回 分身.utcoffset()

    套路 时区名称(分身):
        返回 分身.tzname()

    套路 夏令时(分身):
        返回 分身.dst()

    套路 替换(分身, 时=空, 分=空, 秒=空, 微秒=空, 时区信息=真, *, 折叠=空) -> '〇时间':
        """使用指定的新值返回一个新的时间对象."""
        if 时 is None:
            时 = 分身.hour
        if 分 is None:
            分 = 分身.minute
        if 秒 is None:
            秒 = 分身.second
        if 微秒 is None:
            微秒 = 分身.microsecond
        if 时区信息 is True:
            时区信息 = 分身.tzinfo
        if 折叠 is None:
            折叠 = 分身.fold
        return type(分身)(时, 分, 秒, 微秒, 时区信息, 折叠=折叠)

〇时间.最小值 = 〇时间(0, 0, 0)
〇时间.最大值 = 〇时间(23, 59, 59, 999999)
〇时间.分辨率 = 〇时间差(微秒数=1)


类 〇日时(datetime.datetime, 〇日期):
    """〇日时(年, 月, 日[, 时[, 分[, 秒[, 微秒[, 时区信息]]]]])

    年/月/日 是必须给出的参数. 时区信息 可以为 空 或时区信息子类的实例.
    其余参数可以是整数.
    """

    套路 __new__(本类, 年, 月, 日, 时=0, 分=0, 秒=0, 微秒=0, 时区信息=空, *, 折叠=0):
        返回 datetime.datetime.__new__(本类, 年, 月, 日, hour=时, minute=分,
                second=秒, microsecond=微秒, tzinfo=时区信息, fold=折叠)

    @property
    套路 时(分身):
        "0-23"
        返回 分身.hour

    @property
    套路 分(分身):
        "0-59"
        返回 分身.minute

    @property
    套路 秒(分身):
        "0-59"
        返回 分身.second

    @property
    套路 微秒(分身):
        "0-999999"
        返回 分身.microsecond

    @property
    套路 时区信息(分身):
        返回 分身.tzinfo

    @property
    套路 折叠(分身):
        返回 分身.fold

    @classmethod
    套路 从时间戳(本类, 时间, 时区=空) -> '〇日时':
        "从 时间.时间() 之类的时间戳构造一个日时对象"
        返回 本类.fromtimestamp(时间, tz=时区)

    @classmethod
    套路 从时间戳utc(本类, 时间) -> '〇日时':
        "从时间戳构造一个 UTC 日时对象"
        返回 本类.utcfromtimestamp(时间)

    @classmethod
    套路 此刻(本类, 时区=空) -> '〇日时':
        """返回一个代表当前时间的新日时对象.

        如果未指定 时区, 则使用本地时区.
        """
        返回 本类.now(时区)

    @classmethod
    套路 此刻utc(本类) -> '〇日时':
        "返回一个代表 utc 日期和时间的新日时对象"
        返回 本类.utcnow()

    @classmethod
    套路 组合(本类, 日期, 时间, 时区信息=真) -> '〇日时':
        "将给定的日期和时间组合为一个日时对象"
        if not isinstance(日期, datetime.date):
            raise TypeError("日期参数须为日期类实例")
        if not isinstance(时间, datetime.time):
            raise TypeError("时间参数须为时间类实例")
        if 时区信息 is True:
            时区信息 = 时间.tzinfo
        return 本类(日期.year, 日期.month, 日期.day,
                   时间.hour, 时间.minute, 时间.second, 时间.microsecond,
                   时区信息, 折叠=时间.fold)

    @classmethod
    套路 从iso格式(本类, 日期字符串) -> '〇日时':
        返回 本类.fromisoformat(日期字符串)

    套路 时间元组(分身):
        "返回与 时间.本地时元组() 兼容的本地时间元组"
        返回 时间元组汉化(分身.timetuple())

    套路 时间戳(分身):
        返回 分身.timestamp()

    套路 utc时间元组(分身):
        "返回与 时间.本地时元组() 兼容的 utc 时间元组"
        返回 分身.utctimetuple()

    套路 日期(分身) -> '〇日期':
        "返回日期部分"
        返回 〇日期(分身.年, 分身.月, 分身.日)

    套路 时间(分身) -> '〇时间':
        "返回时间部分"
        返回 〇时间(分身.时, 分身.分, 分身.秒, 分身.微秒, 折叠=分身.折叠)

    套路 时间时区(分身) -> '〇时间':
        "返回时间部分和时区信息"
        返回 〇时间(分身.时, 分身.分, 分身.秒, 分身.微秒, 分身.时区信息, 折叠=分身.折叠)

    套路 替换(分身, 年=空, 月=空, 日=空, 时=空, 分=空, 秒=空, 微秒=空, 时区信息=真, *, 折叠=空) -> '〇日时':
        """使用指定的新值返回一个新的日时对象."""
        if 年 is None:
            年 = 分身.year
        if 月 is None:
            月 = 分身.month
        if 日 is None:
            日 = 分身.day
        if 时 is None:
            时 = 分身.hour
        if 分 is None:
            分 = 分身.minute
        if 秒 is None:
            秒 = 分身.second
        if 微秒 is None:
            微秒 = 分身.microsecond
        if 时区信息 is True:
            时区信息 = 分身.tzinfo
        if 折叠 is None:
            折叠 = 分身.fold
        return type(分身)(年, 月, 日, 时, 分, 秒, 微秒, 时区信息, 折叠=折叠)

    套路 时区调整(分身, 时区=空):  # TODO
        返回 分身.astimezone(时区)

    套路 转字符串(分身):
        "返回一个表示日期和时间的字符串"
        weekday = 分身.toordinal() % 7 or 7
        return "%s %04d 年 %s %d 日 %02d:%02d:%02d" % (
            _日名称[weekday],
            分身.year,
            _月名称[分身.month],
            分身.day,
            分身.hour, 分身.minute, 分身.second)            

    套路 iso格式(分身, 分隔符='T', 时间规格='自动'):
        '''时间规格选项: 自动, 小时数, 分钟数, 秒数, 毫秒数, 微秒数
        
        完整格式为 YYYY-MM-DD HH:MM:SS.mmmmmm

        可选 分隔符 参数指定日期与时间之间的分隔符.

        可选 时间规格 参数指定时间要包括哪些项.
        '''
        时间规格 = _时间规格字典.获取(时间规格, 时间规格)
        返回 分身.isoformat(sep=分隔符, timespec=时间规格)

    @classmethod
    套路 从格式串(本类, 日期字符串, 格式) -> '〇日时':
        返回 本类.strptime(日期字符串, 格式)

    套路 utc偏移量(分身) -> '〇时间差':
        返回 分身.utcoffset()

    套路 时区名称(分身):
        返回 分身.tzname()

    套路 夏令时(分身):
        返回 分身.dst()

    def __sub__(self, other):
        "Subtract two datetimes, or a datetime and a timedelta."
        if not isinstance(other, datetime.datetime):
            if isinstance(other, datetime.timedelta):
                return self + -other
            return NotImplemented

        days1 = self.toordinal()
        days2 = other.toordinal()
        secs1 = self.second + self.minute * 60 + self.hour * 3600
        secs2 = other.second + other.minute * 60 + other.hour * 3600
        base = 〇时间差(days1 - days2,
                         secs1 - secs2,
                         self.microsecond - other.microsecond)
        if self.tzinfo is other.tzinfo:
            return base
        myoff = self.utcoffset()
        otoff = other.utcoffset()
        if myoff == otoff:
            return base
        if myoff is None or otoff is None:
            raise TypeError("不知偏移量的日期时间与知道偏移量的日期时间不能比较")
        return base + otoff - myoff

〇日时.最小值 = 〇日时(1, 1, 1)
〇日时.最大值 = 〇日时(9999, 12, 31, 23, 59, 59, 999999)
〇日时.分辨率 = 〇时间差(微秒数=1)


类 〇时区(〇时区信息):
    __slots__ = '_offset', '_name'

    _Omitted = object()
    def __new__(cls, 偏移量, 名称=_Omitted):
        if not isinstance(偏移量, datetime.timedelta):
            raise TypeError("偏移量须为时间差对象")
        if 名称 is cls._Omitted:
            if not 偏移量:
                return cls.utc
            名称 = None
        elif not isinstance(名称, str):
            raise TypeError("名称须为字符串")
        if not cls._minoffset <= 偏移量 <= cls._maxoffset:
            raise ValueError("偏移量须为时间差对象, "
                             "严格介于 -〇时间差(小时数=24) 和 "
                             "〇时间差(小时数=24) 之间.")
        return cls._create(偏移量, 名称)

    @classmethod
    def _create(cls, offset, name=None):
        self = 〇时区信息.__new__(cls)
        self._offset = offset
        self._name = name
        return self

    def __getinitargs__(self):
        """pickle support"""
        if self._name is None:
            return (self._offset,)
        return (self._offset, self._name)

    def __eq__(self, other):
        if isinstance(other, datetime.timezone):
            return self._offset == other._offset
        return NotImplemented

    def __hash__(self):
        return hash(self._offset)

    def __repr__(self):
        """Convert to formal string, for repr().

        >>> tz = timezone.utc
        >>> repr(tz)
        'datetime.timezone.utc'
        >>> tz = timezone(timedelta(hours=-5), 'EST')
        >>> repr(tz)
        "datetime.timezone(datetime.timedelta(-1, 68400), 'EST')"
        """
        if self is self.utc:
            return '日时.〇时区.utc'
        if self._name is None:
            return "%s.%s(%r)" % (self.__class__.__module__,
                                  self.__class__.__qualname__,
                                  self._offset)
        return "%s.%s(%r, %r)" % (self.__class__.__module__,
                                  self.__class__.__qualname__,
                                  self._offset, self._name)

    def __str__(self):
        return self.时区名称(None)

    套路 utc偏移量(分身, 日期时间):
        if isinstance(日期时间, datetime.datetime) or 日期时间 is None:
            return 分身._offset
        raise TypeError("utc偏移量() 参数须为日时类实例"
                        "或为空")

    套路 时区名称(分身, 日期时间):
        if isinstance(日期时间, datetime.datetime) or 日期时间 is None:
            if 分身._name is None:
                return 分身._name_from_offset(分身._offset)
            return 分身._name
        raise TypeError("时区名称() 参数须为日时类实例"
                        "或为空")

    套路 夏令时(分身, 日期时间):
        if isinstance(日期时间, datetime.datetime) or 日期时间 is None:
            return None
        raise TypeError("夏令时() 参数须为日时类实例"
                        "或为空")

    套路 从utc(分身, 日期时间):
        if isinstance(日期时间, datetime.datetime):
            if 日期时间.tzinfo is not 分身:
                raise ValueError("从utc: 日期时间.时区信息 "
                                 "不是自身")
            return 日期时间 + 分身._offset
        raise TypeError("从utc() 参数须为日时类实例"
                        "或为空")

    _maxoffset = 〇时间差(小时数=24, 毫秒数=-1)
    _minoffset = -_maxoffset

    @staticmethod
    def _name_from_offset(delta):
        if not delta:
            return 'UTC'
        if delta < 〇时间差(0):
            sign = '-'
            delta = -delta
        else:
            sign = '+'
        hours, rest = divmod(delta, 〇时间差(小时数=1))
        minutes, rest = divmod(rest, 〇时间差(分钟数=1))
        seconds = rest.seconds
        microseconds = rest.microseconds
        if microseconds:
            return (f'UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'
                    f'.{microseconds:06d}')
        if seconds:
            return f'UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'
        return f'UTC{sign}{hours:02d}:{minutes:02d}'

〇时区.utc = datetime.timezone.utc
〇时区.最小值 = datetime.timezone.min
〇时区.最大值 = datetime.timezone.max
