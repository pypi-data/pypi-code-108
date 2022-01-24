from datetime import datetime

STANDARD_FORMAT = {
    'isoDateTime': '%Y-%m-%dT%H:%M:%SZ',
    'datetime': '%Y-%m-%d %H:%M:%S',
    'date': '%Y-%m-%d',
    'time': '%H:%M:%S',
    'month': '%Y-%m',
    'dbdt': '%Y%m%d_%H%M%S'
}


class Date:
    @classmethod
    def format(cls, in_date=None, in_fmt='datetime'):
        date = in_date or datetime.now()
        fmt = STANDARD_FORMAT[in_fmt] or in_fmt
        return date.strftime(fmt)

    @classmethod
    def now(cls):
        return int(datetime.now().timestamp())

    @classmethod
    def create(cls, target):
        if type(target) is str:
            return datetime.fromisoformat(target)
        if type(target) is int:
            return datetime.fromtimestamp(target)
        if type(target) is datetime:
            return target
        return None
