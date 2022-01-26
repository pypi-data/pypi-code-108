from typing import Tuple

import arrow


class Axe:
    def __init__(self):
        ...

    def parse(self, date_str: str) -> arrow.arrow.Arrow:
        '''support format 1970-09-09, 1970-09-09T0303, 1970/09/09 0303, 1970/09/09T0303,
        1970.01.01 etc
        '''
        return arrow.get(date_str)

    def diff(self, date1: str, date2: str) -> Tuple[int]:
        diff = self.parse(date2) - self.parse(date1)
        hour, reminder = divmod(diff.seconds, 3600)
        minute, second = divmod(reminder, 60)
        return diff.days, hour, minute, second

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
