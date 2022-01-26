from os.path import expanduser
from datetime import datetime, timedelta


class Tools:
    @classmethod
    def extend_path(cls, path: str):
        return expanduser(path)


class TimeSection:
    __time_type = dict(year=1, month=2, days=3, hours=4, minutes=5, seconds=6)
    __datetime_format = "%Y:%m:%d:%H:%M:%S"

    @classmethod
    def nowstamp_point(cls, time_delta: int = 0, time_type: str = "hours", res_func=int):
        """
        :param time_type: days/hours/minutes/seconds
        :param time_delta: timedelta offset
        :param res_func: format timestamp
        :return: timestamp
        """
        time_delta = timedelta(**{time_type: time_delta})
        timestamp = (datetime.now() + time_delta).timestamp()
        return cls.timestamp_point(timestamp, time_type, res_func)

    @classmethod
    def timestamp_point(cls, time_stamp: float, time_type: str = "hours", res_func=int):
        point = cls.__time_type[time_type]
        now = datetime.fromtimestamp(time_stamp)
        date_string = ":".join(now.strftime(cls.__datetime_format).split(':')[:point]) + cls.__fill_format(point)
        return res_func(datetime.strptime(date_string, cls.__datetime_format).timestamp())

    @classmethod
    def __fill_format(cls, point: int):
        return ":00"*(len(cls.__time_type) - point)
