"some function for misc"


from datetime import datetime
from typing import Any, Callable, Iterable, Union

_all = all
_any = any


def all(iterable: Iterable, func: Callable[[Any], bool] = None) -> bool:
    """like buildin all(iterable), can accept an test function"""
    if func is None:
        return _all(iterable)

    for it in iterable:
        if not func(it):
            return False

    return True


def any(iterable: Iterable, func: Callable[[Any], bool] = None) -> bool:
    """like buildin any(iterable), can accept an test function"""
    if func is None:
        return _any(iterable)

    for it in iterable:
        if func(it):
            return True

    return False


def parse_datetime(timestr: Union[str, datetime]) -> datetime:
    """
    parse str to datatime

    support format:
    - 2021-12-27 10:31:30
    - 2021/12/27 10:31:30
    - 2021/12/27 03:31
    - 2021/12/27 3:31
    """
    if isinstance(timestr, datetime):
        return timestr

    assert isinstance(
        timestr, str
    ), f"Type Error timestr must be str or datetime, timestr:{type(timestr)}"

    timearr = timestr.replace("-", " ").replace("/", " ").replace(":", " ").split(" ")
    assert len(timearr) == 5 or len(timearr) == 6
    timeintarr: list[Any] = list([int(n) for n in timearr])
    if len(timeintarr) == 5:
        timeintarr.append(0)
    return datetime(*timeintarr)
