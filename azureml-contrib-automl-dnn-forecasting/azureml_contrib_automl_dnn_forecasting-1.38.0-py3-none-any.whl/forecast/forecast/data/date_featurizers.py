"""A variety of means for transforming a DatetimeIndex into a numerical feature for the model."""

import abc

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar


class DateFeaturizer(abc.ABC):
    """Base class from which all date featurizers are derived."""

    @abc.abstractmethod
    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Transforms a pandas.DatetimeIndex into a numpy array based on a property of the datetime.

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """A human-readable name for the feature.

        Returns
        -------
        str

        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def num_values(self) -> int:
        """The number of unique integral values the feature can assume.

        Returns
        -------
        int

        """
        raise NotImplementedError


class NormalizedFeaturizer(DateFeaturizer):
    """Maps an index feature in the range [0, N-1] to the range [-1, 1]."""

    def __init__(self, featurizer: DateFeaturizer):
        """Wraps a featurizer for mapping to the range [-1, 1].

        Parameters
        ----------
        featurizer: DateFeaturizer
            The featurizer to wrap

        """
        self._featurizer = featurizer

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the wrapped index feature to the range [-1, 1].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return self._featurizer(dt) / (self._featurizer.num_values - 1) - 0.5

    @property
    def name(self) -> str:
        """The name of the featurizer appended with '_normalized'.

        Returns
        -------
        str

        """
        return self._featurizer.name + '_normalized'

    @property
    def num_values(self) -> int:
        """The number of unique integral values the wrapped featurizer may assume (0 as the values are mapped to float).

        Returns
        -------
        int

        """
        return 0


class SecondOfMinuteFeaturizer(DateFeaturizer):
    """Returns the second in the current minute of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the second of the datetime to a float in the range [0, 59].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.second.map(float).values

    @property
    def name(self) -> str:
        """The name of the featurizer ('second_of_minute').

        Returns
        -------
        str

        """
        return 'second_of_minute'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (60).

        Returns
        -------
        int

        """
        return 60


class MinuteOfHourFeaturizer(DateFeaturizer):
    """Returns the minute in the current hour of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the minute of the datetime to a float in the range [0, 59].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.minute.map(float).values

    @property
    def name(self) -> str:
        """The name of the featurizer ('minute_of_hour').

        Returns
        -------
        str

        """
        return 'minute_of_hour'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (60).

        Returns
        -------
        int

        """
        return 60


class HourOfDayFeaturizer(DateFeaturizer):
    """Returns the hour in the current day of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the hour of the datetime to a float in the range [0, 23].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.hour.map(float).values

    @property
    def name(self) -> str:
        """The name of the featurizer ('hour_of_day').

        Returns
        -------
        str

        """
        return 'hour_of_day'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (24).

        Returns
        -------
        int

        """
        return 24


class DayOfWeekFeaturizer(DateFeaturizer):
    """Returns the day in the current week of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the day of the datetime to a float in the range [0, 6].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.dayofweek.map(float).values

    @property
    def name(self) -> str:
        """The name of the featurizer ('day_of_week').

        Returns
        -------
        str

        """
        return 'day_of_week'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (7).

        Returns
        -------
        int

        """
        return 7


class DayOfMonthFeaturizer(DateFeaturizer):
    """Returns the day in the current month of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the day of the datetime to a float in the range [0, 30].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.day.map(float).values - 1

    @property
    def name(self) -> str:
        """The name of the featurizer ('day_of_month').

        Returns
        -------
        str

        """
        return 'day_of_month'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (31).

        Returns
        -------
        int

        """
        return 31


class DayOfYearFeaturizer(DateFeaturizer):
    """Returns the day in the current year of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the day of the datetime to a float in the range [0, 365].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.dayofyear.map(float).values - 1

    @property
    def name(self) -> str:
        """The name of the featurizer ('day_of_year').

        Returns
        -------
        str

        """
        return 'day_of_year'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (366).

        Returns
        -------
        int

        """
        return 366  # note: we must include years that have leap years to ensure embedddings function correctly


class WeekOfYearFeaturizer(DateFeaturizer):
    """Returns the week in the current year of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the week of the datetime to a float in the range [0, 52].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.weekofyear.map(float).values - 1

    @property
    def name(self) -> str:
        """The name of the featurizer ('week_of_year').

        Returns
        -------
        str

        """
        return 'week_of_year'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (53).

        Returns
        -------
        int

        """
        return 53


class MonthOfYearFeaturizer(DateFeaturizer):
    """Returns the month in the current year of the specified datetime."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the month of the datetime to a float in the range [0, 11].

        Parameters
        ----------
        dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        return dt.month.map(float).values - 1

    @property
    def name(self) -> str:
        """The name of the featurizer ('month_of_year').

        Returns
        -------
        str

        """
        return 'month_of_year'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (12).

        Returns
        -------
        int

        """
        return 12


class HolidayFeaturizer(DateFeaturizer):
    """Returns the value 1 if the day is a US Federal Holiday and 0 otherwise."""

    def __call__(self, dt: pd.DatetimeIndex) -> np.ndarray:
        """Maps the datetime to a boolean indicating whether the datetime's date is a US Federal Holiday.

        Parameters
        ----------
         dt: pd.DatetimeIndex
            The datetimes to transform

        Returns
        -------
        np.ndarray

        """
        start_dt = dt.date.min()
        end_dt = dt.date.max()
        holidays = {d.date() for d in USFederalHolidayCalendar().holidays(start_dt, end_dt)}
        return dt.isin(holidays).astype(float)

    @property
    def name(self) -> str:
        """The name of the featurizer ('holiday').

        Returns
        -------
        str

        """
        return 'holiday'

    @property
    def num_values(self) -> int:
        """The number of unique values the featurized values may assume (2).

        Returns
        -------
        int

        """
        return 2
