"""Utils to generate fake data.

Notes
-----
At the time of writing we're using python 3.5.5, which does not meet Faker
requirements (python >= 3.6). Consider refactoring this module with Faker
when in the next python upgrade.
See https://faker.readthedocs.io/en/master/index.html
"""

import itertools
import random
import string
import typing as tp
from datetime import datetime, timedelta

from bambooapi_client.model.period import Period
from bambooapi_client.model.value import Value


T = tp.TypeVar('T')


def list_(
    model: tp.Union[tp.Any, tp.Callable],
    length: int,
    **kwargs
) -> tp.Callable[[], list]:
    """Return a callable that returns n instances of model.

    Examples
    --------
    >>> list_(dict, 2, foo='bar')()
    [{'foo': 'bar'}, {'foo': 'bar'}]
    """
    def callable_() -> list:
        return [
            model(**kwargs) if callable(model) else model
            for _ in range(length)
        ]

    return callable_


def random_choice(seq: tp.Sequence[T]) -> tp.Callable[[], T]:
    """Return a callable that returns a random choice.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_choice(['foo', 'bar', 'baz'])()
    'bar'
    """
    def callable_() -> str:
        return random.choice(seq)
    return callable_


def random_string(length: int = 8) -> tp.Callable[[], str]:
    """Return a callable that returns strings of the given length.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_string(5)()
    '0UAqF'
    """
    def callable_() -> str:
        return ''.join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )
    return callable_


def random_float(min_: float, max_: float) -> tp.Callable[[], float]:
    """Return a callable that returns uniform random floats within a range.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> round(random_float(min_=15.0, max_=42.0)(), 5)
    37.79939
    """
    def callable_() -> float:
        return random.uniform(a=min_, b=max_)

    return callable_


def random_int(min_: int, max_: int) -> tp.Callable[[], int]:
    """Return a callable that returns uniform random ints within a range.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_int(min_=15, max_=42)()
    42
    """
    def callable_() -> int:
        return random.randint(a=min_, b=max_)

    return callable_


def random_country() -> tp.Callable[[], str]:
    """Return a callable that returns a random country.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_country()()
    'Italy'
    """

    def callable_() -> str:
        countries = ['Spain', 'France', 'Germany', 'Italy', ' Switzerland']
        return random.choice(countries)

    return callable_


def random_country_code() -> tp.Callable[[], str]:
    """Return a callable that returns a random country code.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_country_code()()
    'IT'
    """

    def callable_() -> str:
        country_codes = ['ES', 'FR', 'DE', 'IT', 'CH']
        return random.choice(country_codes)

    return callable_


def incremental_id(start: int = 0) -> tp.Callable[[], int]:
    """Return a callable that returns incremental ids on each call.

    Examples
    --------
    >>> _callable = incremental_id(start=42)
    >>> _callable()
    42
    >>> _callable()
    43
    """
    iterator = itertools.count(start)

    def callable_() -> int:
        return next(iterator)

    return callable_


def incremental_datetime(
    start: datetime = datetime.utcnow(),
    increment: timedelta = timedelta(minutes=1),
) -> tp.Callable[[], datetime]:
    """Return a callable that returns incremental datetimes on each call.

    Examples
    --------
    >>> from datetime import datetime
    >>> _callable = incremental_datetime(start=datetime(2021, 5, 1))
    >>> _callable()
    datetime.datetime(2021, 5, 1, 0, 0)
    >>> _callable()
    datetime.datetime(2021, 5, 1, 0, 1)
    """
    def generator(_start, _increment):
        while True:
            yield _start
            _start += _increment

    iterator = iter(generator(start, increment))

    def callable_() -> datetime:
        return next(iterator)

    return callable_


def tariff_period_value(
    min_: float = 0.0,
    max_: float = 10.0,
    units='kW',
) -> tp.Callable[[], Value]:
    """Return a callable that returns a new Value on each call.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> _callable = tariff_period_value()
    >>> _callable()
    {'units': 'kW', 'value': 8.444218515250482}
    """

    def callable_() -> Value:
        return Value(
            value=random.uniform(min_, max_),
            units=units,
        )

    return callable_


def tariff_period(
    value: float = random_float(0.0, 10.0),
) -> tp.Callable[[], Period]:
    """Return a callable that returns a new Period on each call.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> _callable = tariff_period()
    >>> isinstance(_callable(), Period)
    True
    """
    def callable_() -> Period:
        return Period(
            type='foo',
            power=tariff_period_value(units='kW')(),
            energy=tariff_period_value(units='EUR/kWh')(),
        )

    return callable_


def tariff_periods(
    names: tp.List[str],
) -> tp.Callable[[], tp.Dict[str, Period]]:
    """Return a callable that returns a Periods dict on each call.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> _callable = tariff_periods(names=['P1', 'P2', 'P3'])
    >>> periods = _callable()
    >>> sorted(periods.keys())
    ['P1', 'P2', 'P3']
    >>> [isinstance(v, Period) for v in periods.values()]
    [True, True, True]
    """

    def callable_() -> tp.Dict[str, Period]:
        periods_list = list_(tariff_period(), length=len(names))()
        return {name: period for name, period in zip(names, periods_list)}

    return callable_


def tariff_timetable(
    periods_names: tp.List[str],
    keys: tp.List[str] = ('winter', 'summer', 'weekend_holiday'),
) -> tp.Callable[[], tp.Dict[str, tp.List[str]]]:
    """Return callable that returns a timetable dict on each call.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> _callable = tariff_timetable(
    ...     periods_names=['P1', 'P2', 'P3'],
    ...     keys=['winter', 'summer', 'weekend_holiday'],
    ... )
    >>> _callable()
    {'winter': ['P3', 'P3', 'P2', 'P1', 'P2', 'P2', 'P3', 'P1', 'P2', 'P2', 'P3', 'P2', 'P1', 'P3', 'P2', 'P1', 'P3', 'P3', 'P3', 'P3', 'P1', 'P3', 'P3', 'P3'], 'summer': ['P2', 'P1', 'P2', 'P2', 'P3', 'P3', 'P2', 'P3', 'P1', 'P3', 'P2', 'P1', 'P3', 'P2', 'P3', 'P3', 'P1', 'P2', 'P3', 'P1', 'P1', 'P3', 'P1', 'P2'], 'weekend_holiday': ['P1', 'P3', 'P3', 'P2', 'P1', 'P1', 'P2', 'P3', 'P1', 'P2', 'P3', 'P2', 'P3', 'P2', 'P3', 'P2', 'P2', 'P2', 'P2', 'P2', 'P2', 'P1', 'P1', 'P1']}
    """  # noqa: E501
    def callable_() -> tp.Dict[str, tp.List[str]]:
        return {key: random.choices(periods_names, k=24) for key in keys}

    return callable_
