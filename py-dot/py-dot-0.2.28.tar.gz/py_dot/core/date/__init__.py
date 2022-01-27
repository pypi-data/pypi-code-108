import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Union

_PERIOD = r'^([+-]?\d+(?:\.\d+)?)?~([+-]?\d+(?:\.\d+)?)?$'

_DIGIT_TIMESTAMP = r'^([+-])?(\d{4})(\d\d)(\d\d)(?:(\d\d)(?:(\d\d)(?:(\d\d)(\d+)?)?)?)?(?:\.(\d+))?$'

now = time.time()
TIMEZONE_OFFSET_HOUR = (datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)).total_seconds() / 3600


class Period:
    begin: datetime = None
    end: datetime = None

    _duration_time: int

    @property
    def duration_time(self) -> int:
        if not hasattr(self, '_duration_time'):
            self._duration_time = int((self.end - self.begin).total_seconds())

        return self._duration_time

    def __init__(
        self,
        period_string: str = None,
        matched: re.Match = None,
        begin: Union[str, datetime] = None,
        end: Union[str, datetime] = None,
        use_default_timezone=None
    ):
        if not (period_string or matched or begin or end):
            raise ValueError('`begin`, `end` or `period_string` is required.')

        if matched is None:
            matched = is_period_string(period_string)

            if matched is None:
                raise ValueError('Invalid Period String:' + period_string)

        if matched:
            begin, end = matched.groups()

        if begin:
            self.begin = from_digit_timestamp(begin, use_default_timezone=use_default_timezone)

        if end:
            self.end = from_digit_timestamp(end, use_default_timezone=use_default_timezone, to_end=True)

    def __str__(self):
        begin = self.begin
        end = self.end

        if begin and end:
            return f"{begin.__str__()}~{end.__str__()}"

        if begin:
            return begin.__str__() + '~'

        return '~' + end.__str__()

    def split(self, seconds: int) -> List['Period']:
        pass


@dataclass
class DateParts:
    y: str
    m: str
    d: str
    h: str
    i: str

    def __init__(self, time: datetime):
        self.y = str(time.year).rjust(2, '0')
        self.m = str(time.month).rjust(2, '0')
        self.d = str(time.day).rjust(2, '0')
        self.h = str(time.hour).rjust(2, '0')
        self.i = str(time.minute).rjust(2, '0')


def is_digit_timestamp(timestamp_string: str) -> re.Match:
    """ Check the String be Digit Timestamp-able String

    :param timestamp_string:
    """
    return re.fullmatch(_DIGIT_TIMESTAMP, timestamp_string)


def _get_part(value: int, default: int):
    return value if value else default


def from_digit_timestamp(
    timestamp_string: str,
    matched: re.Match = -1,
    use_default_timezone=False,
    to_end=False
) -> datetime:
    """ Get Datetime from Digit Timestamp String

    UTC:

    - 12341212
    - 1234121213
    - 123412121212
    - 12341212121212
    - 12341212121212123

    +12:

    - 12341212121212123.12

    -12:

    - -12341212121212123.12

    :param timestamp_string:
    :param matched:
    :param use_default_timezone: Using Default Timezone when has not Timezone Digit
    """
    if matched == -1:
        matched = is_digit_timestamp(timestamp_string)

    if matched is None:
        raise ValueError(f'Invalid Digit Timestamp String: {timestamp_string}')

    flag, y, m, d, h, i, s, u, z = matched.groups()

    timezone_hours = 0
    if z:
        timezone_hours = int(z) if flag != '-' else -int(z)
    elif use_default_timezone:
        timezone_hours = TIMEZONE_OFFSET_HOUR

    return datetime(
        int(y),
        int(m),
        int(d),
        int(_get_part(h, 23 if to_end else 0)),
        int(_get_part(i, 59 if to_end else 0)),
        int(_get_part(s, 59 if to_end else 0)),
        int(_get_part(u, 999999 if to_end else 0)),
        tzinfo=timezone(
            timedelta(
                hours=timezone_hours
            )
        )
    )


def is_period_string(period_string: str) -> Union[re.Match, None]:
    """ Check the String be Period-able String
    """
    if period_string != '~':
        return re.fullmatch(_PERIOD, period_string)

    return None

# def from_period_string(period_string: str, matched: re.Match = -1) -> Period:
#     """ Get Begin and End Date from Period Expression String
#
#     - [DIGIT_TIMESTAMP]~[DIGIT_TIMESTAMP]
#     - [DIGIT_TIMESTAMP]~
#     - ~[DIGIT_TIMESTAMP]
#
#     :param period_string:
#     :param matched:
#     """
#     if matched == -1:
#         matched = is_period_string(period_string)
#
#     if matched is None:
#         raise ValueError(f'Invalid Period String: {period_string}')
#
#     return Period(matched[0], matched[1])
