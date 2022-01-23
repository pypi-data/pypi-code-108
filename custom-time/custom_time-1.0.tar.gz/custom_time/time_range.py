# encoding=utf-8
# @Time    : 2022/1/23 15:49
# @Author  : YangBiao
# @Email   : 19921297590@126.com
# @File    : time_range
# @Version : 1.0
# @Python  : python 3.7.2

from .custom_time import CustomTime

class TimeRange:

    def __init__(self, start_time, end_time, years=0, months=0, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        # type: (CustomTime, CustomTime, int, int, int ,int,int,int,int,int,int) -> None
        self._step = (years, months, days, seconds, microseconds, milliseconds, minutes, hours, weeks)

        self._start_time = start_time
        self._end_time = end_time
        self._current = start_time.delta(*[-i for i in self._step])

        self._count = 0

    def __iter__(self):
        return self

    def __next__(self):
        current = self._current.delta(*self._step)
        if self._start_time <= current < self._end_time:
            self._current = current
            self._count += 1
            return self._current
        else:
            raise StopIteration

    @property
    def count(self):
        return self._count
