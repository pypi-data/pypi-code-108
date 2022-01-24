#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import abc
from datetime import datetime

import pandas as pd
import trafaret as t

from datarobot._compat import Int, String
from datarobot.client import get_client, staticproperty
from datarobot.enums import (
    CV_METHOD,
    DEFAULT_MAX_WAIT,
    DIFFERENCING_METHOD,
    PERIODICITY_MAX_TIME_STEP,
    SERIES_AGGREGATION_TYPE,
    TIME_UNITS,
    TREAT_AS_EXPONENTIAL,
)
from datarobot.errors import InvalidUsageError
from datarobot.utils import from_api, parse_time
from datarobot.utils.waiters import wait_for_async_resolution

__all__ = (
    "RandomCV",
    "StratifiedCV",
    "GroupCV",
    "UserCV",
    "RandomTVH",
    "UserTVH",
    "StratifiedTVH",
    "GroupTVH",
    "DatetimePartitioning",
    "DatetimePartitioningSpecification",
    "BacktestSpecification",
    "FeatureSettings",
    "Periodicity",
)


def get_class(cv_method, validation_type):
    if cv_method == CV_METHOD.DATETIME:
        raise ValueError("Cannot get_class for {} - use DatetimePartitioning.preview instead")
    classes = {
        "CV": {
            CV_METHOD.RANDOM: RandomCV,
            CV_METHOD.STRATIFIED: StratifiedCV,
            CV_METHOD.USER: UserCV,
            CV_METHOD.GROUP: GroupCV,
        },
        "TVH": {
            CV_METHOD.RANDOM: RandomTVH,
            CV_METHOD.STRATIFIED: StratifiedTVH,
            CV_METHOD.USER: UserTVH,
            CV_METHOD.GROUP: GroupTVH,
        },
    }
    try:
        return classes[validation_type][cv_method]
    except KeyError:
        err_msg = "Error in getting class for cv_method={} and validation_type={}"
        raise ValueError(err_msg.format(cv_method, validation_type))


class PartitioningMethod(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collect_payload(self):
        """ Set up the dict that should be sent to the server when setting the target
        Returns
        -------
        partitioning_spec : dict
        """
        return {}

    @abc.abstractmethod
    def prep_payload(self, project_id, max_wait=DEFAULT_MAX_WAIT):
        """ Run any necessary validation and prep of the payload, including async operations

        Mainly used for the datetime partitioning spec but implemented in general for consistency
        """
        pass


class BasePartitioningMethod(PartitioningMethod):

    """This is base class to describe partitioning method
    with options"""

    cv_method = None
    validation_type = None
    seed = 0
    _data = None
    _static_fields = frozenset(["cv_method", "validation_type"])

    def __init__(self, cv_method, validation_type, seed=0):
        self.cv_method = cv_method
        self.validation_type = validation_type
        self.seed = seed

    def collect_payload(self):
        keys = (
            "cv_method",
            "validation_type",
            "reps",
            "user_partition_col",
            "training_level",
            "validation_level",
            "holdout_level",
            "cv_holdout_level",
            "seed",
            "validation_pct",
            "holdout_pct",
            "partition_key_cols",
        )
        if not self._data:
            self._data = {key: getattr(self, key, None) for key in keys}
        return self._data

    def prep_payload(self, project_id, max_wait=DEFAULT_MAX_WAIT):
        pass

    def __repr__(self):
        if self._data:
            payload = {
                k: v
                for k, v in self._data.items()
                if v is not None and k not in self._static_fields
            }
        else:
            self.collect_payload()
            return repr(self)
        return "{}({})".format(self.__class__.__name__, payload)

    @classmethod
    def from_data(cls, data):
        """Can be used to instantiate the correct class of partitioning class
        based on the data
        """
        if data is None:
            return None
        cv_method = data.get("cv_method")
        validation_type = data.get("validation_type")
        other_params = {
            key: value for key, value in data.items() if key not in ["cv_method", "validation_type"]
        }
        return get_class(cv_method, validation_type)(**other_params)


class BaseCrossValidation(BasePartitioningMethod):
    cv_method = None
    validation_type = "CV"

    def __init__(self, cv_method, validation_type="CV"):
        self.cv_method = cv_method  # pragma: no cover
        self.validation_type = validation_type  # pragma: no cover


class BaseTVH(BasePartitioningMethod):
    cv_method = None
    validation_type = "TVH"

    def __init__(self, cv_method, validation_type="TVH"):
        self.cv_method = cv_method  # pragma: no cover
        self.validation_type = validation_type  # pragma: no cover


class RandomCV(BaseCrossValidation):
    """A partition in which observations are randomly assigned to cross-validation groups
    and the holdout set.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    seed : int
        a seed to use for randomization
    """

    cv_method = "random"

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedCV(BaseCrossValidation):
    """A partition in which observations are randomly assigned to cross-validation groups
    and the holdout set, preserving in each group the same ratio of positive to negative cases as in
    the original data.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    seed : int
        a seed to use for randomization
    """

    cv_method = "stratified"

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupCV(BaseCrossValidation):
    """ A partition in which one column is specified, and rows sharing a common value
    for that column are guaranteed to stay together in the partitioning into cross-validation
    groups and the holdout set.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    partition_key_cols : list
        a list containing a single string, where the string is the name of the column whose
        values should remain together in partitioning
    seed : int
        a seed to use for randomization
    """

    cv_method = "group"

    def __init__(self, holdout_pct, reps, partition_key_cols, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserCV(BaseCrossValidation):
    """ A partition where the cross-validation folds and the holdout set are specified by
    the user.

    Parameters
    ----------
    user_partition_col : string
        the name of the column containing the partition assignments
    cv_holdout_level
        the value of the partition column indicating a row is part of the holdout set
    seed : int
        a seed to use for randomization
    """

    cv_method = "user"

    def __init__(self, user_partition_col, cv_holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.cv_holdout_level = cv_holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class RandomTVH(BaseTVH):
    """Specifies a partitioning method in which rows are randomly assigned to training, validation,
    and holdout.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    seed : int
        a seed to use for randomization
    """

    cv_method = "random"

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserTVH(BaseTVH):
    """Specifies a partitioning method in which rows are assigned by the user to training,
    validation, and holdout sets.

    Parameters
    ----------
    user_partition_col : string
        the name of the column containing the partition assignments
    training_level
        the value of the partition column indicating a row is part of the training set
    validation_level
        the value of the partition column indicating a row is part of the validation set
    holdout_level
        the value of the partition column indicating a row is part of the holdout set (use
        None if you want no holdout set)
    seed : int
        a seed to use for randomization
    """

    cv_method = "user"

    def __init__(self, user_partition_col, training_level, validation_level, holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.training_level = training_level  # pragma: no cover
        self.validation_level = validation_level  # pragma: no cover
        self.holdout_level = holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedTVH(BaseTVH):
    """A partition in which observations are randomly assigned to train, validation, and
    holdout sets, preserving in each group the same ratio of positive to negative cases as in the
    original data.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    seed : int
        a seed to use for randomization
    """

    cv_method = "stratified"

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupTVH(BaseTVH):
    """A partition in which one column is specified, and rows sharing a common value
    for that column are guaranteed to stay together in the partitioning into the training,
    validation, and holdout sets.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    partition_key_cols : list
        a list containing a single string, where the string is the name of the column whose
        values should remain together in partitioning
    seed : int
        a seed to use for randomization
    """

    cv_method = "group"

    def __init__(self, holdout_pct, validation_pct, partition_key_cols, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover


def construct_duration_string(years=0, months=0, days=0, hours=0, minutes=0, seconds=0):
    """ Construct a valid string representing a duration in accordance with ISO8601

    A duration of six months, 3 days, and 12 hours could be represented as P6M3DT12H.

    Parameters
    ----------
    years : int
        the number of years in the duration
    months : int
        the number of months in the duration
    days : int
        the number of days in the duration
    hours : int
        the number of hours in the duration
    minutes : int
        the number of minutes in the duration
    seconds : int
        the number of seconds in the duration

    Returns
    -------
    duration_string: str
        The duration string, specified compatibly with ISO8601
    """
    return "P{}Y{}M{}DT{}H{}M{}S".format(years, months, days, hours, minutes, seconds)


_periodicity_converter = t.Dict(
    {
        t.Key("time_steps"): Int(gte=0, lte=PERIODICITY_MAX_TIME_STEP),
        t.Key("time_unit"): t.Enum(
            TIME_UNITS.MILLISECOND,
            TIME_UNITS.SECOND,
            TIME_UNITS.MINUTE,
            TIME_UNITS.HOUR,
            TIME_UNITS.DAY,
            TIME_UNITS.WEEK,
            TIME_UNITS.MONTH,
            TIME_UNITS.QUARTER,
            TIME_UNITS.YEAR,
            u"ROW",
        ),
    }
).ignore_extra("*")


class Periodicity(object):
    """
    Periodicity configuration

    Parameters
    ----------
    time_steps : int
        Time step value
    time_unit : string
        Time step unit, valid options are values from `datarobot.enums.TIME_UNITS`

    Examples
    --------
    .. code-block:: python

        from datarobot as dr
        periodicities = [
            dr.Periodicity(time_steps=10, time_unit=dr.enums.TIME_UNITS.HOUR),
            dr.Periodicity(time_steps=600, time_unit=dr.enums.TIME_UNITS.MINUTE)]
        spec = dr.DatetimePartitioningSpecification(
            # ...
            periodicities=periodicities
        )

    """

    def __init__(self, time_steps, time_unit):
        _periodicity_converter.check({"time_steps": time_steps, "time_unit": time_unit})
        self.time_steps = time_steps
        self.time_unit = time_unit

    def __eq__(self, other):
        return self.time_steps == other.time_steps and self.time_unit == other.time_unit

    def collect_payload(self):
        return {"time_steps": self.time_steps, "time_unit": self.time_unit}


_feature_settings_converter = t.Dict(
    {
        t.Key("feature_name"): String(),
        t.Key("known_in_advance", optional=True, default=None): t.Bool() | t.Null,
        t.Key("do_not_derive", optional=True, default=None): t.Bool() | t.Null,
    }
).ignore_extra("*")


class FeatureSettings(object):
    """ Per feature settings

    Attributes
    ----------
    feature_name : string
        name of the feature
    known_in_advance : bool
        (New in version v2.11) Optional, for time series projects
        only. Sets whether the feature is known in advance, i.e., values for future dates are known
        at prediction time. If not specified, the feature uses the value from the
        `default_to_known_in_advance` flag.
    do_not_derive : bool
        (New in v2.17) Optional, for time series projects only.
        Sets whether the feature is excluded from feature derivation. If not
        specified, the feature uses the value from the `default_to_do_not_derive` flag.
    """

    def __init__(self, feature_name, known_in_advance=None, do_not_derive=None):
        _feature_settings_converter.check(
            {
                "feature_name": feature_name,
                "known_in_advance": known_in_advance,
                "do_not_derive": do_not_derive,
            }
        )

        self.feature_name = feature_name
        self.known_in_advance = known_in_advance
        self.do_not_derive = do_not_derive

    @classmethod
    def from_server_data(cls, feature_name, known_in_advance=None, do_not_derive=None):
        return cls(feature_name, known_in_advance=known_in_advance, do_not_derive=do_not_derive)

    def collect_payload(self):
        return {
            "feature_name": self.feature_name,
            "known_in_advance": self.known_in_advance,
            "do_not_derive": self.do_not_derive,
        }

    def __eq__(self, other):
        return (
            self.feature_name == other.feature_name
            and self.known_in_advance == other.known_in_advance
            and self.do_not_derive == other.do_not_derive
        )

    def __repr__(self):
        return (
            "FeatureSettings(feature_name='{feature_name}', "
            "known_in_advance={kia}, do_not_derive={dnd})"
        ).format(feature_name=self.feature_name, kia=self.known_in_advance, dnd=self.do_not_derive)


_backtest_converter = t.Dict(
    {
        t.Key("index"): Int(),
        t.Key("available_training_start_date"): parse_time,
        t.Key("available_training_duration"): String(),
        t.Key("available_training_row_count", optional=True): Int(),
        t.Key("available_training_end_date"): parse_time,
        t.Key("primary_training_start_date"): parse_time,
        t.Key("primary_training_duration"): String(),
        t.Key("primary_training_row_count", optional=True): Int(),
        t.Key("primary_training_end_date"): parse_time,
        t.Key("gap_start_date"): parse_time,
        t.Key("gap_duration"): String(),
        t.Key("gap_row_count", optional=True): Int(),
        t.Key("gap_end_date"): parse_time,
        t.Key("validation_start_date"): parse_time,
        t.Key("validation_duration"): String(),
        t.Key("validation_row_count", optional=True): Int(),
        t.Key("validation_end_date"): parse_time,
        t.Key("total_row_count", optional=True): Int(),
    }
).ignore_extra("*")

_duration_backtest_fields = {"gap_duration", "validation_start_date", "validation_duration"}
_start_end_backtest_fields = {
    "primary_training_start_date",
    "primary_training_end_date",
    "validation_start_date",
    "validation_end_date",
}


class BacktestSpecification(object):
    """ Uniquely defines a Backtest used in a DatetimePartitioning

    Includes only the attributes of a backtest directly controllable by users.  The other attributes
    are assigned by the DataRobot application based on the project dataset and the user-controlled
    settings.

    There are two ways to specify an individual backtest:

    Option 1: Use ``index``, ``gap_duration``, ``validation_start_date``, and
    ``valiidation_duration``. All durations should be specified with a duration string such as those
    returned by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.

    .. code-block:: python

        import datarobot as dr

        partitioning_spec = dr.DatetimePartitioningSpecification(
            backtests=[
                # modify the first backtest using option 1
                dr.BacktestSpecification(
                    index=0,
                    gap_duration=dr.partitioning_methods.construct_duration_string(),
                    validation_start_date=datetime(year=2010, month=1, day=1),
                    validation_duration=dr.partitioning_methods.construct_duration_string(years=1),
                )
            ],
            # other partitioning settings...
        )

    Option 2 (New in version v2.20): Use ``index``, ``primary_training_start_date``,
    ``primary_training_end_date``, ``validation_start_date``, and ``validation_end_date``. In this
    case, note that setting ``primary_training_end_date`` and ``validation_start_date`` to the same
    timestamp will result with no gap being created.

    .. code-block:: python

        import datarobot as dr

        partitioning_spec = dr.DatetimePartitioningSpecification(
            backtests=[
                # modify the first backtest using option 2
                dr.BacktestSpecification(
                    index=0,
                    primary_training_start_date=datetime(year=2005, month=1, day=1),
                    primary_training_end_date=datetime(year=2010, month=1, day=1),
                    validation_start_date=datetime(year=2010, month=1, day=1),
                    validation_end_date=datetime(year=2011, month=1, day=1),
                )
            ],
            # other partitioning settings...
        )

    All durations should be specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Attributes
    ----------
    index : int
        the index of the backtest to update
    gap_duration : str
        a duration string specifying the desired duration of the gap between
        training and validation scoring data for the backtest
    validation_start_date : datetime.datetime
        the desired start date of the validation scoring data for this backtest
    validation_duration : str
        a duration string specifying the desired duration of the validation
        scoring data for this backtest
    validation_end_date : datetime.datetime
        the desired end date of the validation scoring data for this backtest
    primary_training_start_date : datetime.datetime
        the desired start date of the training partition for this backtest
    primary_training_end_date : datetime.datetime
        the desired end date of the training partition for this backtest
    """

    def __init__(
        self,
        index,
        gap_duration=None,
        validation_start_date=None,
        validation_duration=None,
        validation_end_date=None,
        primary_training_start_date=None,
        primary_training_end_date=None,
    ):
        self.index = index
        self.gap_duration = gap_duration
        self.validation_start_date = validation_start_date
        self.validation_duration = validation_duration
        self.validation_end_date = validation_end_date
        self.primary_training_start_date = primary_training_start_date
        self.primary_training_end_date = primary_training_end_date

    def _validate_datetimes(self):
        for field in _start_end_backtest_fields:
            if getattr(self, field, None) and not isinstance(getattr(self, field), datetime):
                raise ValueError("expected {} to be a datetime.datetime".format(field))

    def collect_payload(self):
        self._validate_datetimes()
        payload = {"index": self.index}
        if all(getattr(self, field, None) for field in _duration_backtest_fields):
            payload.update(
                {field: getattr(self, field, None) for field in _duration_backtest_fields}
            )
        elif all(getattr(self, field, None) for field in _start_end_backtest_fields):
            payload.update(
                {field: getattr(self, field, None) for field in _start_end_backtest_fields}
            )
        else:
            raise InvalidUsageError(
                "Only one of (gap_duration, validation_duration, validation_start_date) or "
                "(validation_start_date, validation_end_date, primary_training_start_date, "
                "primary_training_end_date) can be used to configure backtests."
            )

        return payload


class Backtest(object):
    """ A backtest used to evaluate models trained in a datetime partitioned project

    When setting up a datetime partitioning project, backtests are specified by a
    :class:`BacktestSpecification <datarobot.BacktestSpecification>`.

    The available training data corresponds to all the data available for training, while the
    primary training data corresponds to the data that can be used to train while ensuring that all
    backtests are available.  If a model is trained with more data than is available in the primary
    training data, then all backtests may not have scores available.

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Attributes
    ----------
    index : int
        the index of the backtest
    available_training_start_date : datetime.datetime
        the start date of the available training data for this backtest
    available_training_duration : str
        the duration of available training data for this backtest
    available_training_row_count : int or None
        the number of rows of available training data for this backtest.  Only available when
        retrieving from a project where the target is set.
    available_training_end_date : datetime.datetime
        the end date of the available training data for this backtest
    primary_training_start_date : datetime.datetime
        the start date of the primary training data for this backtest
    primary_training_duration : str
        the duration of the primary training data for this backtest
    primary_training_row_count : int or None
        the number of rows of primary training data for this backtest.  Only available when
        retrieving from a project where the target is set.
    primary_training_end_date : datetime.datetime
        the end date of the primary training data for this backtest
    gap_start_date : datetime.datetime
        the start date of the gap between training and validation scoring data for this backtest
    gap_duration : str
        the duration of the gap between training and validation scoring data for this backtest
    gap_row_count : int or None
        the number of rows in the gap between training and validation scoring data for this
        backtest.  Only available when retrieving from a project where the target is set.
    gap_end_date : datetime.datetime
        the end date of the gap between training and validation scoring data for this backtest
    validation_start_date : datetime.datetime
        the start date of the validation scoring data for this backtest
    validation_duration : str
        the duration of the validation scoring data for this backtest
    validation_row_count : int or None
        the number of rows of validation scoring data for this backtest.  Only available when
        retrieving from a project where the target is set.
    validation_end_date : datetime.datetime
        the end date of the validation scoring data for this backtest
    total_row_count : int or None
        the number of rows in this backtest.  Only available when retrieving from a project where
        the target is set.
    """

    def __init__(
        self,
        index=None,
        available_training_start_date=None,
        available_training_duration=None,
        available_training_row_count=None,
        available_training_end_date=None,
        primary_training_start_date=None,
        primary_training_duration=None,
        primary_training_row_count=None,
        primary_training_end_date=None,
        gap_start_date=None,
        gap_duration=None,
        gap_row_count=None,
        gap_end_date=None,
        validation_start_date=None,
        validation_duration=None,
        validation_row_count=None,
        validation_end_date=None,
        total_row_count=None,
    ):
        self.index = index
        self.available_training_start_date = available_training_start_date
        self.available_training_duration = available_training_duration
        self.available_training_row_count = available_training_row_count
        self.available_training_end_date = available_training_end_date
        self.primary_training_start_date = primary_training_start_date
        self.primary_training_duration = primary_training_duration
        self.primary_training_row_count = primary_training_row_count
        self.primary_training_end_date = primary_training_end_date
        self.gap_start_date = gap_start_date
        self.gap_duration = gap_duration
        self.gap_row_count = gap_row_count
        self.gap_end_date = gap_end_date
        self.validation_start_date = validation_start_date
        self.validation_duration = validation_duration
        self.validation_row_count = validation_row_count
        self.validation_end_date = validation_end_date
        self.total_row_count = total_row_count

    def to_specification(self, use_start_end_format=False):
        """ Render this backtest as a
        :class:`BacktestSpecification <datarobot.BacktestSpecification>`.

        The resulting specification includes only the attributes users can directly control, not
        those indirectly determined by the project dataset.

        Parameters
        ----------
        use_start_end_format : bool
            Default ``False``. If ``False``, will use a duration-based approach for specifying
            backtests (``gap_duration``, ``validation_start_date``, and ``validation_duration``).
            If ``True``, will use a start/end date approach for specifying
            backtests (``primary_training_start_date``, ``primary_training_end_date``,
            ``validation_start_date``, ``validation_end_date``).

        Returns
        -------
        BacktestSpecification
            the specification for this backtest
        """
        if use_start_end_format:
            return BacktestSpecification(
                self.index,
                primary_training_start_date=self.primary_training_start_date,
                primary_training_end_date=self.primary_training_end_date,
                validation_start_date=self.validation_start_date,
                validation_end_date=self.validation_end_date,
            )
        else:
            return BacktestSpecification(
                self.index, self.gap_duration, self.validation_start_date, self.validation_duration
            )

    def to_dataframe(self):
        """ Render this backtest as a dataframe for convenience of display

        Returns
        -------
        backtest_partitioning : pandas.Dataframe
            the backtest attributes, formatted into a dataframe
        """
        display_dict = {
            "start_date": {
                "backtest_{}_available_training".format(
                    self.index
                ): self.available_training_start_date,
                "backtest_{}_primary_training".format(self.index): self.primary_training_start_date,
                "backtest_{}_gap".format(self.index): self.gap_start_date,
                "backtest_{}_validation".format(self.index): self.validation_start_date,
            },
            "duration": {
                "backtest_{}_available_training".format(
                    self.index
                ): self.available_training_duration,
                "backtest_{}_primary_training".format(self.index): self.primary_training_duration,
                "backtest_{}_gap".format(self.index): self.gap_duration,
                "backtest_{}_validation".format(self.index): self.validation_duration,
            },
            "end_date": {
                "backtest_{}_available_training".format(
                    self.index
                ): self.available_training_end_date,
                "backtest_{}_primary_training".format(self.index): self.primary_training_end_date,
                "backtest_{}_gap".format(self.index): self.gap_end_date,
                "backtest_{}_validation".format(self.index): self.validation_end_date,
            },
        }
        return pd.DataFrame.from_dict(display_dict)

    @classmethod
    def from_data(cls, data):
        data = _backtest_converter.check(data)
        return cls(**data)


class DatetimePartitioningSpecification(PartitioningMethod):
    """ Uniquely defines a DatetimePartitioning for some project

    Includes only the attributes of DatetimePartitioning that are directly controllable by users,
    not those determined by the DataRobot application based on the project dataset and the
    user-controlled settings.

    This is the specification that should be passed to :meth:`Project.set_target
    <datarobot.models.Project.set_target>` via the ``partitioning_method`` parameter. To see the
    full partitioning based on the project dataset, use :meth:`DatetimePartitioning.generate
    <datarobot.DatetimePartitioning.generate>`.

    All durations should be specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Note that either (``holdout_start_date``, ``holdout_duration``) or (``holdout_start_date``,
    ``holdout_end_date``) can be used to specify holdout partitioning settings.

    Attributes
    ----------
    datetime_partition_column : str
        the name of the column whose values as dates are used to assign a row
        to a particular partition
    autopilot_data_selection_method : str
        one of ``datarobot.enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD``.  Whether models created
        by the autopilot should use "rowCount" or "duration" as their data_selection_method.
    validation_duration : str or None
        the default validation_duration for the backtests
    holdout_start_date : datetime.datetime or None
        The start date of holdout scoring data.  If ``holdout_start_date`` is specified,
        either ``holdout_duration`` or ``holdout_end_date`` must also be specified. If
        ``disable_holdout`` is set to ``True``, ``holdout_start_date``, ``holdout_duration``, and
        ``holdout_end_date`` may not be specified.
    holdout_duration : str or None
        The duration of the holdout scoring data.  If ``holdout_duration`` is specified,
        ``holdout_start_date`` must also be specified.  If ``disable_holdout`` is set to ``True``,
        ``holdout_duration``, ``holdout_start_date``, and ``holdout_end_date`` may not be specified.
    holdout_end_date : datetime.datetime or None
        The end date of holdout scoring data.  If ``holdout_end_date`` is specified,
        ``holdout_start_date`` must also be specified.  If ``disable_holdout`` is set to ``True``,
        ``holdout_end_date``, ``holdout_start_date``, and ``holdout_duration`` may not be specified.
    disable_holdout : bool or None
        (New in version v2.8) Whether to suppress allocating a holdout fold.
        If set to ``True``, ``holdout_start_date``, ``holdout_duration``, and ``holdout_end_date``
        may not be specified.
    gap_duration : str or None
        The duration of the gap between training and holdout scoring data
    number_of_backtests : int or None
        the number of backtests to  use
    backtests : list of :class:`BacktestSpecification <datarobot.BacktestSpecification>`
        the exact specification of backtests to use.  The indexes of the specified backtests should
        range from 0 to number_of_backtests - 1.  If any backtest is left unspecified, a default
        configuration will be chosen.
    use_time_series : bool
        (New in version v2.8) Whether to create a time series project (if ``True``) or an OTV
        project which uses datetime partitioning (if ``False``).  The default behaviour is to create
        an OTV project.
    default_to_known_in_advance : bool
        (New in version v2.11) Optional, default ``False``. Used for time series projects only. Sets
        whether all features default to being treated as known in advance. Known in advance features
        are expected to be known for dates in the future when making predictions, e.g., "is this a
        holiday?". Individual features can be set to a value different than the default using the
        ``feature_settings`` parameter.
    default_to_do_not_derive : bool
        (New in v2.17) Optional, default ``False``. Used for time series projects only. Sets whether
        all features default to being treated as do-not-derive features, excluding them from feature
        derivation. Individual features can be set to a value different than the default by using
        the ``feature_settings`` parameter.
    feature_derivation_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define how
        far back relative to the forecast point the feature derivation window should start.
        Expressed in terms of the ``windows_basis_unit`` and should be negative or zero.
    feature_derivation_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define how
        far back relative to the forecast point the feature derivation window should end.  Expressed
        in terms of the ``windows_basis_unit`` and should be a positive value.
    feature_settings : list of :py:class:`FeatureSettings <datarobot.FeatureSettings>`
        (New in version v2.9) Optional, a list specifying per feature settings, can be
        left unspecified.
    forecast_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should start.  Expressed
        in terms of the ``windows_basis_unit``.
    forecast_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should end.  Expressed
        in terms of the ``windows_basis_unit``.
    windows_basis_unit : string, optional
        (New in version v2.14) Only used for time series projects. Indicates which unit is
        a basis for feature derivation window and forecast window. Valid options are detected time
        unit (one of the ``datarobot.enums.TIME_UNITS``) or "ROW".
        If omitted, the default value is the detected time unit.
    treat_as_exponential : string, optional
        (New in version v2.9) defaults to "auto". Used to specify whether to treat data
        as exponential trend and apply transformations like log-transform. Use values from the
        ``datarobot.enums.TREAT_AS_EXPONENTIAL`` enum.
    differencing_method : string, optional
        (New in version v2.9) defaults to "auto". Used to specify which differencing method to
        apply of case if data is stationary. Use values from
        ``datarobot.enums.DIFFERENCING_METHOD`` enum.
    periodicities : list of Periodicity, optional
        (New in version v2.9) a list of :py:class:`datarobot.Periodicity`. Periodicities units
        should be "ROW", if the ``windows_basis_unit`` is "ROW".
    multiseries_id_columns : list of str or null
        (New in version v2.11) a list of the names of multiseries id columns to define series
        within the training data.  Currently only one multiseries id column is supported.
    use_cross_series_features : bool
        (New in version v2.14) Whether to use cross series features.
    aggregation_type : str, optional
        (New in version v2.14) The aggregation type to apply when creating
        cross series features. Optional, must be one of "total" or "average".
    cross_series_group_by_columns : list of str, optional
        (New in version v2.15) List of columns (currently of length 1).
        Optional setting that indicates how to further split series into
        related groups. For example, if every series is sales of an individual product, the series
        group-by could be the product category with values like "men's clothing",
        "sports equipment", etc.. Can only be used in a multiseries project with
        ``use_cross_series_features`` set to ``True``.
    calendar_id : str, optional
        (New in version v2.15) The id of the :py:class:`CalendarFile <datarobot.CalendarFile>` to
        use with this project.
    unsupervised_mode: bool, optional
        (New in version v2.20) defaults to False, indicates whether partitioning should be
        constructed for the unsupervised project.
    model_splits: int, optional
        (New in version v2.21) Sets the cap on the number of jobs per model used when
        building models to control number of jobs in the queue. Higher number of model splits
        will allow for less downsampling leading to the use of more post-processed data.
    allow_partial_history_time_series_predictions: bool, optional
        (New in version v2.24) Wheter to allow time series models to make predictions using
        partial historical data.
    """

    def __init__(
        self,
        datetime_partition_column,
        autopilot_data_selection_method=None,
        validation_duration=None,
        holdout_start_date=None,
        holdout_duration=None,
        disable_holdout=None,
        gap_duration=None,
        number_of_backtests=None,
        backtests=None,
        use_time_series=False,
        default_to_known_in_advance=False,
        default_to_do_not_derive=False,
        feature_derivation_window_start=None,
        feature_derivation_window_end=None,
        feature_settings=None,
        forecast_window_start=None,
        forecast_window_end=None,
        windows_basis_unit=None,
        treat_as_exponential=None,
        differencing_method=None,
        periodicities=None,
        multiseries_id_columns=None,
        use_cross_series_features=None,
        aggregation_type=None,
        cross_series_group_by_columns=None,
        calendar_id=None,
        holdout_end_date=None,
        unsupervised_mode=False,
        model_splits=None,
        allow_partial_history_time_series_predictions=False,
    ):
        self.datetime_partition_column = datetime_partition_column
        self.autopilot_data_selection_method = autopilot_data_selection_method
        self.validation_duration = validation_duration
        self.holdout_start_date = holdout_start_date
        self.holdout_duration = holdout_duration
        self.holdout_end_date = holdout_end_date
        self.disable_holdout = disable_holdout
        self.gap_duration = gap_duration
        self.number_of_backtests = number_of_backtests
        self.backtests = backtests or []
        self.use_time_series = use_time_series
        self.default_to_known_in_advance = default_to_known_in_advance
        self.default_to_do_not_derive = default_to_do_not_derive
        self.feature_derivation_window_start = feature_derivation_window_start
        self.feature_derivation_window_end = feature_derivation_window_end
        self.windows_basis_unit = windows_basis_unit
        self.feature_settings = feature_settings
        self.forecast_window_start = forecast_window_start
        self.forecast_window_end = forecast_window_end
        self.treat_as_exponential = treat_as_exponential
        self.differencing_method = differencing_method
        self.periodicities = periodicities
        self.multiseries_id_columns = multiseries_id_columns
        self.use_cross_series_features = use_cross_series_features
        self.aggregation_type = aggregation_type
        self.cross_series_group_by_columns = cross_series_group_by_columns
        self.calendar_id = calendar_id
        self.unsupervised_mode = unsupervised_mode
        self.model_splits = model_splits
        self.allow_partial_history_time_series_predictions = (
            allow_partial_history_time_series_predictions
        )

    def collect_payload(self):
        if self.holdout_start_date and not isinstance(self.holdout_start_date, datetime):
            raise ValueError("expected holdout_start_date to be a datetime.datetime")
        if self.holdout_end_date and not isinstance(self.holdout_end_date, datetime):
            raise ValueError("expected holdout_end_date to be a datetime.datetime")
        if self.holdout_duration and self.holdout_end_date:
            raise InvalidUsageError(
                'Only one of "holdout_duration" and "holdout_end_date" can be used to specify '
                "holdout partitioning settings."
            )
        feature_settings = (
            [fs.collect_payload() for fs in self.feature_settings]
            if self.feature_settings
            else None
        )
        periodicities = (
            [p.collect_payload() for p in self.periodicities] if self.periodicities else None
        )
        payload = {
            "datetime_partition_column": self.datetime_partition_column,
            "autopilot_data_selection_method": self.autopilot_data_selection_method,
            "validation_duration": self.validation_duration,
            "holdout_start_date": self.holdout_start_date,
            "disable_holdout": self.disable_holdout,
            "gap_duration": self.gap_duration,
            "number_of_backtests": self.number_of_backtests,
            "backtests": [bt.collect_payload() for bt in self.backtests] or None,
            "use_time_series": self.use_time_series,
            "default_to_known_in_advance": self.default_to_known_in_advance,
            "default_to_do_not_derive": self.default_to_do_not_derive,
            "feature_derivation_window_start": self.feature_derivation_window_start,
            "feature_derivation_window_end": self.feature_derivation_window_end,
            "feature_settings": feature_settings,
            "forecast_window_start": self.forecast_window_start,
            "forecast_window_end": self.forecast_window_end,
            "windows_basis_unit": self.windows_basis_unit,
            "cv_method": CV_METHOD.DATETIME,
            "multiseries_id_columns": self.multiseries_id_columns,
            "treat_as_exponential": self.treat_as_exponential,
            "differencing_method": self.differencing_method,
            "periodicities": periodicities,
            "use_cross_series_features": self.use_cross_series_features,
            "aggregation_type": self.aggregation_type,
            "cross_series_group_by_columns": self.cross_series_group_by_columns,
            "calendar_id": self.calendar_id,
            "model_splits": self.model_splits,
            "allow_partial_history_time_series_predictions": (
                self.allow_partial_history_time_series_predictions
            ),
        }
        if self.unsupervised_mode:
            payload["unsupervised_mode"] = self.unsupervised_mode
        if self.holdout_duration:
            payload["holdout_duration"] = self.holdout_duration
        elif self.holdout_end_date:
            payload["holdout_end_date"] = self.holdout_end_date

        return payload

    def prep_payload(self, project_id, max_wait=DEFAULT_MAX_WAIT):
        if not self.multiseries_id_columns:
            return
        from datarobot.models.feature import Feature

        datetime_part = Feature.get(project_id, self.datetime_partition_column)
        props = datetime_part.get_multiseries_properties(
            self.multiseries_id_columns, max_wait=max_wait
        )
        if not props["time_series_eligible"]:
            msg = (
                "The selected datetime partition and multiseries id columns are not eligible for"
                " time series modeling, i.e. they are insufficiently unique or regular"
            )
            raise InvalidUsageError(msg)

        if self.use_cross_series_features and self.cross_series_group_by_columns:
            multiseries_id = Feature.get(project_id, self.multiseries_id_columns[0])
            res = multiseries_id.get_cross_series_properties(
                self.datetime_partition_column,
                self.cross_series_group_by_columns,
                max_wait=max_wait,
            )
            if not res["isEligible"]:
                msg = (
                    "The selected cross-series group-by column is not eligible for"
                    " given multiseries id column for time series modeling."
                )
                raise InvalidUsageError(msg)


class DatetimePartitioning(object):
    """ Full partitioning of a project for datetime partitioning.

    To instantiate, use
    :meth:`DatetimePartitioning.get(project_id) <datarobot.DatetimePartitioning.get>`.

    Includes both the attributes specified by the user, as well as those determined by the DataRobot
    application based on the project dataset.  In order to use a partitioning to set the target,
    call :meth:`to_specification <datarobot.DatetimePartitioning.to_specification>` and pass the
    resulting
    :class:`DatetimePartitioningSpecification <datarobot.DatetimePartitioningSpecification>` to
    :meth:`Project.set_target <datarobot.models.Project.set_target>` via the ``partitioning_method``
    parameter.

    The available training data corresponds to all the data available for training, while the
    primary training data corresponds to the data that can be used to train while ensuring that all
    backtests are available.  If a model is trained with more data than is available in the primary
    training data, then all backtests may not have scores available.

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.


    Attributes
    ----------
    project_id : str
        the id of the project this partitioning applies to
    datetime_partition_column : str
        the name of the column whose values as dates are used to assign a row
        to a particular partition
    date_format : str
        the format (e.g. "%Y-%m-%d %H:%M:%S") by which the partition column was interpreted
        (compatible with `strftime <https://docs.python.org/2/library/time.html#time.strftime>`_)
    autopilot_data_selection_method : str
        one of ``datarobot.enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD``.  Whether models created
        by the autopilot use "rowCount" or "duration" as their data_selection_method.
    validation_duration : str or None
        the validation duration specified when initializing the partitioning - not directly
        significant if the backtests have been modified, but used as the default validation_duration
        for the backtests. Can be absent if this is a time series project with an irregular primary
        date/time feature.
    available_training_start_date : datetime.datetime
        The start date of the available training data for scoring the holdout
    available_training_duration : str
        The duration of the available training data for scoring the holdout
    available_training_row_count : int or None
        The number of rows in the available training data for scoring the holdout.  Only available
        when retrieving the partitioning after setting the target.
    available_training_end_date : datetime.datetime
        The end date of the available training data for scoring the holdout
    primary_training_start_date : datetime.datetime or None
        The start date of primary training data for scoring the holdout.
        Unavailable when the holdout fold is disabled.
    primary_training_duration : str
        The duration of the primary training data for scoring the holdout
    primary_training_row_count : int or None
        The number of rows in the primary training data for scoring the holdout.  Only available
        when retrieving the partitioning after setting the target.
    primary_training_end_date : datetime.datetime or None
        The end date of the primary training data for scoring the holdout.
        Unavailable when the holdout fold is disabled.
    gap_start_date : datetime.datetime or None
        The start date of the gap between training and holdout scoring data.
        Unavailable when the holdout fold is disabled.
    gap_duration : str
        The duration of the gap between training and holdout scoring data
    gap_row_count : int or None
        The number of rows in the gap between training and holdout scoring data.  Only available
        when retrieving the partitioning after setting the target.
    gap_end_date : datetime.datetime or None
        The end date of the gap between training and holdout scoring data.
        Unavailable when the holdout fold is disabled.
    disable_holdout : bool or None
        Whether to suppress allocating a holdout fold.
        If set to ``True``, ``holdout_start_date``, ``holdout_duration``, and ``holdout_end_date``
        may not be specified.
    holdout_start_date : datetime.datetime or None
        The start date of holdout scoring data.
        Unavailable when the holdout fold is disabled.
    holdout_duration : str
        The duration of the holdout scoring data
    holdout_row_count : int or None
        The number of rows in the holdout scoring data.  Only available when retrieving the
        partitioning after setting the target.
    holdout_end_date : datetime.datetime or None
        The end date of the holdout scoring data. Unavailable when the holdout fold is disabled.
    number_of_backtests : int
        the number of backtests used.
    backtests : list of :class:`Backtest <datarobot.helpers.partitioning_methods.Backtest>`
        the configured backtests.
    total_row_count : int
        the number of rows in the project dataset.  Only available when retrieving the partitioning
        after setting the target.
    use_time_series : bool
        (New in version v2.8) Whether to create a time series project (if ``True``) or an OTV
        project which uses datetime partitioning (if ``False``).  The default behaviour is to create
        an OTV project.
    default_to_known_in_advance : bool
        (New in version v2.11) Optional, default ``False``. Used for time series projects only. Sets
        whether all features default to being treated as known in advance. Known in advance features
        are expected to be known for dates in the future when making predictions, e.g., "is this a
        holiday?". Individual features can be set to a value different from the default using the
        ``feature_settings`` parameter.
    default_to_do_not_derive : bool
        (New in v2.17) Optional, default ``False``. Used for time series projects only. Sets whether
        all features default to being treated as do-not-derive features, excluding them from feature
        derivation. Individual features can be set to a value different from the default by using
        the ``feature_settings`` parameter.
    feature_derivation_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define
        how far back relative to the forecast point the feature derivation window should start.
        Expressed in terms of the ``windows_basis_unit``.
    feature_derivation_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define how
        far back relative to the forecast point the feature derivation window should end. Expressed
        in terms of the ``windows_basis_unit``.
    feature_settings : list of :py:class:`FeatureSettings <datarobot.FeatureSettings>`
        (New in version v2.9) Optional, a list specifying per feature settings, can be
        left unspecified.
    forecast_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should start. Expressed
        in terms of the ``windows_basis_unit``.
    forecast_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should end. Expressed in
        terms of the ``windows_basis_unit``.
    windows_basis_unit : string, optional
        (New in version v2.14) Only used for time series projects. Indicates which unit is
        a basis for feature derivation window and forecast window. Valid options are detected time
        unit (one of the ``datarobot.enums.TIME_UNITS``) or "ROW".
        If omitted, the default value is detected time unit.
    treat_as_exponential : string, optional
        (New in version v2.9) defaults to "auto". Used to specify whether to treat data
        as exponential trend and apply transformations like log-transform. Use values from the
        ``datarobot.enums.TREAT_AS_EXPONENTIAL`` enum.
    differencing_method : string, optional
        (New in version v2.9) defaults to "auto". Used to specify which differencing method to
        apply of case if data is stationary. Use values from the
        ``datarobot.enums.DIFFERENCING_METHOD`` enum.
    periodicities : list of Periodicity, optional
        (New in version v2.9) a list of :py:class:`datarobot.Periodicity`. Periodicities units
        should be "ROW", if the ``windows_basis_unit`` is "ROW".
    multiseries_id_columns : list of str or null
        (New in version v2.11) a list of the names of multiseries id columns to define series
        within the training data.  Currently only one multiseries id column is supported.
    number_of_known_in_advance_features : int
        (New in version v2.14) Number of features that are marked as known in advance.
    number_of_do_not_derive_features : int
        (New in v2.17) Number of features that are excluded from derivation.
    use_cross_series_features : bool
        (New in version v2.14) Whether to use cross series features.
    aggregation_type : str, optional
        (New in version v2.14) The aggregation type to apply when creating cross series
        features. Optional, must be one of "total" or "average".
    cross_series_group_by_columns : list of str, optional
        (New in version v2.15) List of columns (currently of length 1).
        Optional setting that indicates how to further split series into
        related groups. For example, if every series is sales of an individual product, the series
        group-by could be the product category with values like "men's clothing",
        "sports equipment", etc.. Can only be used in a multiseries project with
        ``use_cross_series_features`` set to ``True``.
    calendar_id : str, optional
        (New in version v2.15) Only available for time series projects. The id of the
        :class:`CalendarFile <datarobot.CalendarFile>` to use with this project.
    calendar_name : str, optional
        (New in version v2.17) Only available for time series projects. The name of the
        :class:`CalendarFile <datarobot.CalendarFile>` used with this project.
    model_splits: int, optional
        (New in version v2.21) Sets the cap on the number of jobs per model used when
        building models to control number of jobs in the queue. Higher number of model splits
        will allow for less downsampling leading to the use of more post-processed data.
    allow_partial_history_time_series_predictions: bool, optional
        (New in version v2.24) Wheter to allow time series models to make predictions using
        partial historical data.
    """

    _client = staticproperty(get_client)
    _converter = t.Dict(
        {
            t.Key("project_id"): String(),
            t.Key("datetime_partition_column"): String(),
            t.Key("date_format"): String(),
            t.Key("autopilot_data_selection_method"): String(),
            t.Key("validation_duration", optional=True): String(),
            t.Key("available_training_start_date"): parse_time,
            t.Key("available_training_duration"): String(),
            t.Key("available_training_row_count", optional=True): Int(),
            t.Key("available_training_end_date"): parse_time,
            t.Key("primary_training_start_date", optional=True): parse_time,
            t.Key("primary_training_duration"): String(),
            t.Key("primary_training_row_count", optional=True): Int(),
            t.Key("primary_training_end_date", optional=True): parse_time,
            t.Key("gap_start_date", optional=True): parse_time,
            t.Key("gap_duration"): String(),
            t.Key("gap_row_count", optional=True): Int(),
            t.Key("gap_end_date", optional=True): parse_time,
            t.Key("disable_holdout", optional=True): t.Bool,
            t.Key("holdout_start_date", optional=True): parse_time,
            t.Key("holdout_duration"): String(),
            t.Key("holdout_row_count", optional=True): Int(),
            t.Key("holdout_end_date", optional=True): parse_time,
            t.Key("number_of_backtests"): Int(),
            t.Key("backtests"): t.List(_backtest_converter),
            t.Key("total_row_count", optional=True): Int(),
            t.Key("use_time_series", optional=True, default=False): t.Bool(),
            t.Key("default_to_known_in_advance", optional=True, default=False): t.Bool(),
            t.Key("default_to_do_not_derive", optional=True, default=False): t.Bool(),
            t.Key("feature_derivation_window_start", optional=True): Int(),
            t.Key("feature_derivation_window_end", optional=True): Int(),
            t.Key("feature_settings", optional=True): t.List(_feature_settings_converter),
            t.Key("forecast_window_start", optional=True): Int(),
            t.Key("forecast_window_end", optional=True): Int(),
            t.Key("windows_basis_unit", optional=True): t.Enum(
                TIME_UNITS.MILLISECOND,
                TIME_UNITS.SECOND,
                TIME_UNITS.MINUTE,
                TIME_UNITS.HOUR,
                TIME_UNITS.DAY,
                TIME_UNITS.WEEK,
                TIME_UNITS.MONTH,
                TIME_UNITS.QUARTER,
                TIME_UNITS.YEAR,
                u"ROW",
            ),
            t.Key("treat_as_exponential", optional=True): t.Enum(
                TREAT_AS_EXPONENTIAL.ALWAYS, TREAT_AS_EXPONENTIAL.NEVER, TREAT_AS_EXPONENTIAL.AUTO
            ),
            t.Key("differencing_method", optional=True): t.Enum(
                DIFFERENCING_METHOD.AUTO,
                DIFFERENCING_METHOD.SIMPLE,
                DIFFERENCING_METHOD.NONE,
                DIFFERENCING_METHOD.SEASONAL,
            ),
            t.Key("periodicities", optional=True): t.List(_periodicity_converter),
            t.Key("multiseries_id_columns", optional=True): t.List(String()),
            t.Key("number_of_known_in_advance_features"): Int(),
            t.Key("number_of_do_not_derive_features"): Int(),
            t.Key("use_cross_series_features", optional=True): t.Bool,
            t.Key("aggregation_type", optional=True): t.Enum(
                SERIES_AGGREGATION_TYPE.AVERAGE, SERIES_AGGREGATION_TYPE.TOTAL
            ),
            t.Key("cross_series_group_by_columns", optional=True): t.List(String()),
            t.Key("calendar_id", optional=True): String(),
            t.Key("calendar_name", optional=True): String(),
            t.Key("model_splits", optional=True): Int(),
            t.Key("allow_partial_history_time_series_predictions", optional=True): t.Bool,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id=None,
        datetime_partition_column=None,
        date_format=None,
        autopilot_data_selection_method=None,
        validation_duration=None,
        available_training_start_date=None,
        available_training_duration=None,
        available_training_row_count=None,
        available_training_end_date=None,
        primary_training_start_date=None,
        primary_training_duration=None,
        primary_training_row_count=None,
        primary_training_end_date=None,
        gap_start_date=None,
        gap_duration=None,
        gap_row_count=None,
        gap_end_date=None,
        disable_holdout=None,
        holdout_start_date=None,
        holdout_duration=None,
        holdout_row_count=None,
        holdout_end_date=None,
        number_of_backtests=None,
        backtests=None,
        total_row_count=None,
        use_time_series=False,
        default_to_known_in_advance=False,
        default_to_do_not_derive=False,
        feature_derivation_window_start=None,
        feature_derivation_window_end=None,
        feature_settings=None,
        forecast_window_start=None,
        forecast_window_end=None,
        windows_basis_unit=None,
        treat_as_exponential=None,
        differencing_method=None,
        periodicities=None,
        multiseries_id_columns=None,
        number_of_known_in_advance_features=0,
        number_of_do_not_derive_features=0,
        use_cross_series_features=None,
        aggregation_type=None,
        cross_series_group_by_columns=None,
        calendar_id=None,
        calendar_name=None,
        model_splits=None,
        allow_partial_history_time_series_predictions=False,
    ):
        self.project_id = project_id
        self.datetime_partition_column = datetime_partition_column
        self.date_format = date_format
        self.autopilot_data_selection_method = autopilot_data_selection_method
        self.validation_duration = validation_duration
        self.available_training_start_date = available_training_start_date
        self.available_training_duration = available_training_duration
        self.available_training_row_count = available_training_row_count
        self.available_training_end_date = available_training_end_date
        self.primary_training_start_date = primary_training_start_date
        self.primary_training_duration = primary_training_duration
        self.primary_training_row_count = primary_training_row_count
        self.primary_training_end_date = primary_training_end_date
        self.gap_start_date = gap_start_date
        self.gap_duration = gap_duration
        self.gap_row_count = gap_row_count
        self.gap_end_date = gap_end_date
        self.disable_holdout = disable_holdout
        self.holdout_start_date = holdout_start_date
        self.holdout_duration = holdout_duration
        self.holdout_row_count = holdout_row_count
        self.holdout_end_date = holdout_end_date
        self.number_of_backtests = number_of_backtests
        self.backtests = backtests
        self.total_row_count = total_row_count
        self.use_time_series = use_time_series
        self.default_to_known_in_advance = default_to_known_in_advance
        self.default_to_do_not_derive = default_to_do_not_derive
        self.feature_derivation_window_start = feature_derivation_window_start
        self.feature_derivation_window_end = feature_derivation_window_end
        self.windows_basis_unit = windows_basis_unit
        self.feature_settings = feature_settings
        self.forecast_window_start = forecast_window_start
        self.forecast_window_end = forecast_window_end
        self.treat_as_exponential = treat_as_exponential
        self.differencing_method = differencing_method
        self.periodicities = periodicities
        self.multiseries_id_columns = multiseries_id_columns
        self.number_of_known_in_advance_features = number_of_known_in_advance_features
        self.number_of_do_not_derive_features = number_of_do_not_derive_features
        self.use_cross_series_features = use_cross_series_features
        self.aggregation_type = aggregation_type
        self.cross_series_group_by_columns = cross_series_group_by_columns
        self.calendar_id = calendar_id
        self.calendar_name = calendar_name
        self.model_splits = model_splits
        self.allow_partial_history_time_series_predictions = (
            allow_partial_history_time_series_predictions
        )

    @classmethod
    def from_server_data(cls, data):
        converted_data = cls._converter.check(from_api(data))
        converted_data["backtests"] = [
            Backtest(**backtest_data) for backtest_data in converted_data["backtests"]
        ]
        if "feature_settings" in converted_data:
            converted_data["feature_settings"] = [
                FeatureSettings.from_server_data(**fs) for fs in converted_data["feature_settings"]
            ] or None
        if "periodicities" in converted_data:
            converted_data["periodicities"] = [
                Periodicity(**p) for p in converted_data["periodicities"]
            ]
        return cls(**converted_data)

    @classmethod
    def generate(cls, project_id, spec, max_wait=DEFAULT_MAX_WAIT, target=None):
        """ Preview the full partitioning determined by a DatetimePartitioningSpecification

        Based on the project dataset and the partitioning specification, inspect the full
        partitioning that would be used if the same specification were passed into
        :meth:`Project.set_target <datarobot.models.Project.set_target>`.

        Parameters
        ----------
        project_id : str
            the id of the project
        spec : DatetimePartitioningSpec
            the desired partitioning
        max_wait : int, optional
            For some settings (e.g. generating a partitioning preview for a multiseries project for
            the first time), an asynchronous task must be run to analyze the dataset.  max_wait
            governs the maximum time (in seconds) to wait before giving up.  In all non-multiseries
            projects, this is unused.
        target : str, optional
            the name of the target column. For unsupervised projects target may be None. Providing
            a target will ensure that partitions are correctly optimized for your dataset.

        Returns
        -------
        DatetimePartitioning :
            the full generated partitioning
        """
        if target is None:
            url = "projects/{}/datetimePartitioning/".format(project_id)
            spec.prep_payload(project_id, max_wait=max_wait)
            payload = spec.collect_payload()
            payload.pop("cv_method")
            response = cls._client.post(url, data=payload)
            return cls.from_server_data(response.json())
        else:
            return cls.generate_optimized(
                project_id=project_id, spec=spec, target=target, max_wait=max_wait
            )

    @classmethod
    def get(cls, project_id):
        """ Retrieve the DatetimePartitioning from a project

        Only available if the project has already set the target as a datetime project.

        Parameters
        ----------
        project_id : str
            the id of the project to retrieve partitioning for

        Returns
        -------
        DatetimePartitioning : the full partitioning for the project
        """
        url = "projects/{}/datetimePartitioning/".format(project_id)
        response = cls._client.get(url)
        return cls.from_server_data(response.json())

    @classmethod
    def generate_optimized(cls, project_id, spec, target, max_wait=DEFAULT_MAX_WAIT):
        """ Preview the full partitioning determined by a DatetimePartitioningSpecification

        Based on the project dataset and the partitioning specification, inspect the full
        partitioning that would be used if the same specification were passed into
        `Project.set_target`.

        Parameters
        ----------
        project_id : str
            the id of the project
        spec : DatetimePartitioningSpec
            the desired partitioning
        target : str
            the name of the target column. For unsupervised projects target may be None.
        max_wait : int, optional
            Governs the maximum time (in seconds) to wait before giving up.

        Returns
        -------
        DatetimePartitioning :
            the full generated partitioning
        """
        url = "projects/{}/optimizedDatetimePartitionings/".format(project_id)
        spec.prep_payload(project_id, max_wait=max_wait)
        payload = spec.collect_payload()
        payload.pop("cv_method")

        payload["target"] = target

        response = cls._client.post(url, data=payload)
        finished_url = wait_for_async_resolution(cls._client, response.headers["Location"])
        finished_response = cls._client.get(finished_url)

        return cls.from_server_data(finished_response.json())

    @classmethod
    def get_optimized(cls, project_id, datetime_partitioning_id):
        """ Retrieve an Optimized DatetimePartitioning from a project for the specified
        datetime_partitioning_id. A datetime_partitioning_id is created by using the
        :meth:`generate_optimized<datarobot.DatetimePartitioning.generate_optimized>` function.

        Parameters
        ----------
        project_id : str
            the id of the project to retrieve partitioning for
        datetime_partitioning_id : ObjectId
            the ObjectId associated with the project to retrieve from mongo

        Returns
        -------
        DatetimePartitioning : the full partitioning for the project
        """
        url = "projects/{}/optimizedDatetimePartitionings/{}".format(
            project_id, datetime_partitioning_id
        )
        response = cls._client.get(url)
        return cls.from_server_data(response.json())

    @classmethod
    def feature_log_list(cls, project_id, offset=None, limit=None):
        """ Retrieve the feature derivation log content and log length for a time series project.

        The Time Series Feature Log provides details about the feature generation process for a
        time series project. It includes information about which features are generated and their
        priority, as well as the detected properties of the time series data such as whether the
        series is stationary, and periodicities detected.

        This route is only supported for time series projects that have finished partitioning.

        The feature derivation log will include information about:

        * | Detected stationarity of the series:
          | e.g. 'Series detected as non-stationary'
        * | Detected presence of multiplicative trend in the series:
          | e.g. 'Multiplicative trend detected'
        * | Detected presence of multiplicative trend in the series:
          | e.g.  'Detected periodicities: 7 day'
        * | Maximum number of feature to be generated:
          | e.g. 'Maximum number of feature to be generated is 1440'
        * | Window sizes used in rolling statistics / lag extractors
          | e.g. 'The window sizes chosen to be: 2 months
          | (because the time step is 1 month and Feature Derivation Window is 2 months)'
        * | Features that are specified as known-in-advance
          | e.g. 'Variables treated as apriori: holiday'
        * | Details about why certain variables are transformed in the input data
          | e.g. 'Generating variable "y (log)" from "y" because multiplicative trend
          | is detected'
        * | Details about features generated as timeseries features, and their priority
          | e.g. 'Generating feature "date (actual)" from "date" (priority: 1)'

        Parameters
        ----------
        project_id : str
            project id to retrieve a feature derivation log for.
        offset : int
            optional, defaults is 0, this many results will be skipped.
        limit : int
            optional, defaults to 100, at most this many results are returned. To specify
            no limit, use 0. The default may change without notice.
        """
        url = "projects/{}/timeSeriesFeatureLog/".format(project_id)
        response = cls._client.get(url, params=dict(offset=offset, limit=limit))
        return response.json()

    @classmethod
    def feature_log_retrieve(cls, project_id):
        """ Retrieve the feature derivation log content and log length for a time series project.

        The Time Series Feature Log provides details about the feature generation process for a
        time series project. It includes information about which features are generated and their
        priority, as well as the detected properties of the time series data such as whether the
        series is stationary, and periodicities detected.

        This route is only supported for time series projects that have finished partitioning.

        The feature derivation log will include information about:

        * | Detected stationarity of the series:
          | e.g. 'Series detected as non-stationary'
        * | Detected presence of multiplicative trend in the series:
          | e.g. 'Multiplicative trend detected'
        * | Detected presence of multiplicative trend in the series:
          | e.g.  'Detected periodicities: 7 day'
        * | Maximum number of feature to be generated:
          | e.g. 'Maximum number of feature to be generated is 1440'
        * | Window sizes used in rolling statistics / lag extractors
          | e.g. 'The window sizes chosen to be: 2 months
          | (because the time step is 1 month and Feature Derivation Window is 2 months)'
        * | Features that are specified as known-in-advance
          | e.g. 'Variables treated as apriori: holiday'
        * | Details about why certain variables are transformed in the input data
          | e.g. 'Generating variable "y (log)" from "y" because multiplicative trend
          | is detected'
        * | Details about features generated as timeseries features, and their priority
          | e.g. 'Generating feature "date (actual)" from "date" (priority: 1)'

        Parameters
        ----------
        project_id : str
            project id to retrieve a feature derivation log for.
        """
        url = "projects/{}/timeSeriesFeatureLog/file/".format(project_id)
        response = cls._client.get(url)
        return response.text

    def to_specification(
        self, use_holdout_start_end_format=False, use_backtest_start_end_format=False
    ):
        """ Render the DatetimePartitioning as a :class:`DatetimePartitioningSpecification
        <datarobot.DatetimePartitioningSpecification>`

        The resulting specification can be used when setting the target, and contains only the
        attributes directly controllable by users.

        Parameters
        ----------
        use_holdout_start_end_format : bool, optional
            Defaults to ``False``. If ``True``, will use ``holdout_end_date`` when configuring the
            holdout partition. If ``False``, will use ``holdout_duration`` instead.
        use_backtest_start_end_format : bool, optional
            Defaults to ``False``. If ``False``, will use a duration-based approach for specifying
            backtests (``gap_duration``, ``validation_start_date``, and ``validation_duration``).
            If ``True``, will use a start/end date approach for specifying
            backtests (``primary_training_start_date``, ``primary_training_end_date``,
            ``validation_start_date``, ``validation_end_date``).

        Returns
        -------
        DatetimePartitioningSpecification
            the specification for this partitioning
        """
        init_data = {
            "datetime_partition_column": self.datetime_partition_column,
            "autopilot_data_selection_method": self.autopilot_data_selection_method,
            "validation_duration": self.validation_duration,
            "holdout_start_date": self.holdout_start_date,
            "gap_duration": self.gap_duration,
            "number_of_backtests": self.number_of_backtests,
            "backtests": [
                bt.to_specification(use_backtest_start_end_format) for bt in self.backtests
            ],
            "use_time_series": self.use_time_series,
            "default_to_known_in_advance": self.default_to_known_in_advance,
            "default_to_do_not_derive": self.default_to_do_not_derive,
            "feature_derivation_window_start": self.feature_derivation_window_start,
            "feature_derivation_window_end": self.feature_derivation_window_end,
            "forecast_window_start": self.forecast_window_start,
            "forecast_window_end": self.forecast_window_end,
            "windows_basis_unit": self.windows_basis_unit,
            "treat_as_exponential": self.treat_as_exponential,
            "differencing_method": self.differencing_method,
            "periodicities": self.periodicities,
            "multiseries_id_columns": self.multiseries_id_columns,
            "feature_settings": self.feature_settings,
            "use_cross_series_features": self.use_cross_series_features,
            "aggregation_type": self.aggregation_type,
            "cross_series_group_by_columns": self.cross_series_group_by_columns,
            "calendar_id": self.calendar_id,
            "model_splits": self.model_splits,
            "disable_holdout": self.disable_holdout,
            "allow_partial_history_time_series_predictions": (
                self.allow_partial_history_time_series_predictions
            ),
        }
        if use_holdout_start_end_format:
            init_data["holdout_end_date"] = self.holdout_end_date
        else:
            init_data["holdout_duration"] = self.holdout_duration

        return DatetimePartitioningSpecification(**init_data)

    def to_dataframe(self):
        """ Render the partitioning settings as a dataframe for convenience of display

        Excludes project_id, datetime_partition_column, date_format,
        autopilot_data_selection_method, validation_duration,
        and number_of_backtests, as well as the row count information, if present.

        Also excludes the time series specific parameters for use_time_series,
        default_to_known_in_advance, default_to_do_not_derive, and defining the feature
        derivation and forecast windows.
        """
        display_dict = {
            "start_date": {
                "available_training": self.available_training_start_date,
                "primary_training": self.primary_training_start_date,
                "gap": self.gap_start_date,
                "holdout": self.holdout_start_date,
            },
            "duration": {
                "available_training": self.available_training_duration,
                "primary_training": self.primary_training_duration,
                "gap": self.gap_duration,
                "holdout": self.holdout_duration,
            },
            "end_date": {
                "available_training": self.available_training_end_date,
                "primary_training": self.primary_training_end_date,
                "gap": self.gap_end_date,
                "holdout": self.holdout_end_date,
            },
        }
        display_df = pd.DataFrame.from_dict(display_dict)
        final_df = display_df.append([bt.to_dataframe() for bt in self.backtests])
        return final_df
