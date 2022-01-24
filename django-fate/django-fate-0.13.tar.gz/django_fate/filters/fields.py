import datetime


class Field:
    def __init__(self, field=None, lookup=None):
        self._value = None
        self._field = field
        self._lookup = lookup

    def __set__(self, instance, value):
        self._value = value

    def __get__(self, instance, owner):
        if self._lookup:
            return {'__'.join((self._field, self._lookup)): self._value}
        else:
            return {self._field: self._value}


class CharField(Field):
    def __set__(self, instance, value):
        try:
            self._value = str(value)
        except Exception as err:
            raise ValueError('查询参数转化为字符串失败!')


class IntField(Field):
    def __set__(self, instance, value):
        try:
            self._value = int(value)
        except Exception as err:
            raise ValueError('值: {} 转化为整型失败!'.format(value))


class ArrayField(Field):
    def __set__(self, instance, value):
        if isinstance(value, list):
            self._value = value
        elif isinstance(value, str):
            self._value = value.split(',')
        elif value is None:
            self._value = []
        else:
            raise ValueError('值: {} 要求是一个数组，或者逗号分割的字符串'.format(str(value)))


class BoolField(Field):
    def __set__(self, instance, value):
        false_li, true_li = [False, 'false', '0', 0], [True, 'true', '1', 1]
        value = str(value).lower() if isinstance(value, str) else value
        if value not in false_li + true_li:
            raise ValueError('值: {} 必须为 true 或者 false。'.format(str(value)))
        self._value = False if value in false_li else True


class DateTimeField(Field):
    """本函数支持了使用不完整的日期时间来查询DateTimeField"""

    def __set__(self, instance, value):
        try:
            value = value.strip()
            date, *time = value.split(' ')
            # 如果仅仅提供了日期
            if not time:
                date_time = datetime.datetime.strptime(value, '%Y-%m-%d')
                timedelta = datetime.timedelta(days=1)
                self._value = [date_time, date_time + timedelta]
                self._lookup = 'range'
            # 如果提供了时期时间，时间类型有三种1.只提供了小时 2.只提供了分钟3.完整的时分秒
            else:
                time = time[0]
                time_type = len(time.split(':'))
                if time_type == 1:
                    date_time = datetime.datetime.strptime(value, '%Y-%m-%d %H')
                    timedelta = datetime.timedelta(hours=1)
                    self._value = [date_time, date_time + timedelta]
                    self._lookup = 'range'
                elif time_type == 2:
                    date_time = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M')
                    timedelta = datetime.timedelta(minutes=1)
                    self._value = [date_time, date_time + timedelta]
                    self._lookup = 'range'
                elif time_type == 3:
                    date_time = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    self._value = date_time
                else:
                    raise ValueError
        except Exception as err:
            raise ValueError('{} 必须为合法的日期时间格式，请使用 YYYY-MM-DD 或 '
                             'YYYY-MM-DD HH:MM:SS'.format(value))
