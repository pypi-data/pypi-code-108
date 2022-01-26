from typing import List, Tuple

import arrow


class ArrowParser():
    def __init__(self, arrow_obj: arrow):
        self.date = arrow.get(arrow_obj)

    def str2list(self) -> List:
        d = self.date
        return [d.year, d.month, d.day, d.hour, d.minute, d.second]


class Axe:
    ''' An :Axe: class wrapping up arrow
    '''
    def __init__(self, date_str: str = ''):
        if not date_str:
            date_str = arrow.now()
        self.year, self.month, self.day, self.hour, self.minute, self.second = \
            ArrowParser(date_str).str2list()[:]

    @classmethod
    def today(cls) -> str:
        return arrow.now().format('YYYY-MM-DD')

    @classmethod
    def yesterday(cls) -> str:
        return arrow.utcnow().shift(days=-1).format('YYYY-MM-DD')

    def __repr__(self):
        return '\n'.join('{:<7} {}'.format(k.capitalize(), v)
                         for k, v in self.__dict__.items())

    def parse(self, date_str: str) -> arrow.arrow.Arrow:
        '''support format 1970-09-09, 1970-09-09T0303, 1970/09/09 0303, 1970/09/09T0303,
        1970.01.01 etc
        '''
        return arrow.get(date_str).replace(tzinfo='+08:00')

    @classmethod
    def now(cls) -> arrow.arrow.Arrow:
        return arrow.now()

    def diff(self,
             date1: str,
             date2: str,
             seconds_only: bool = False) -> Tuple[int]:
        '''Get time difference between two dates.
        '''
        tofloat = lambda s: self.parse(s).float_timestamp
        diff = int(tofloat(date2) - tofloat(date1))
        if seconds_only:
            return diff

        hour, reminder = divmod(diff, 3600)
        minute, second = divmod(reminder, 60)
        days = diff // (3600 * 24)
        return days, hour, minute, second

    def date(self,
             format_str: str = 'YYYY-MM-DD HH-mm-ss',
             display_time: bool = False) -> str:
        if not display_time:
            format_str = format_str.split('T')[0].split(' ')[0]
        return arrow.now().format(format_str)


if __name__ == '__main__':
    x = Axe()
    date = '2021/8/9'
    aa = arrow.get(date)
    print(aa, type(aa))

    d2 = '2020-12-18 09'
    print(x.diff(d2, date))
    print(x.date(display_time=True))
