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
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import datetime_to_string, encode_utf8_if_py2, from_api, parse_time

from ..enums import (
    DATA_SUBSET,
    DATETIME_TREND_PLOTS_RESOLUTION,
    DATETIME_TREND_PLOTS_STATUS,
    SOURCE_TYPE,
)
from ..utils import underscorize

_metadata_start_end_dates_trafaret = t.Dict(
    {
        t.Key("start_date"): t.Or(t.Null, t.Call(parse_time)),
        t.Key("end_date"): t.Or(t.Null, t.Call(parse_time)),
    }
).ignore_extra("*")

_backtest_holdout_metadata_trafaret = t.Dict(
    {
        t.Key(SOURCE_TYPE.TRAINING): _metadata_start_end_dates_trafaret,
        t.Key(SOURCE_TYPE.VALIDATION): _metadata_start_end_dates_trafaret,
    }
).ignore_extra("*")

_accuracy_anomaly_over_time_plots_status_trafaret = t.Dict(
    {
        t.Key(SOURCE_TYPE.TRAINING): t.Enum(*DATETIME_TREND_PLOTS_STATUS.ALL),
        t.Key(SOURCE_TYPE.VALIDATION): t.Enum(*DATETIME_TREND_PLOTS_STATUS.ALL),
    }
).ignore_extra("*")

_forecast_vs_actual_training_validation_status_trafaret = t.Dict(
    {
        t.Key(underscorize(status), to_name=status, optional=True): t.List(Int)
        for status in DATETIME_TREND_PLOTS_STATUS.ALL
    }
).ignore_extra("*")

_forecast_vs_actual_status_trafaret = t.Dict(
    {
        t.Key(SOURCE_TYPE.TRAINING): _forecast_vs_actual_training_validation_status_trafaret,
        t.Key(SOURCE_TYPE.VALIDATION): _forecast_vs_actual_training_validation_status_trafaret,
    }
).ignore_extra("*")

_accuracy_over_time_plots_bin_trafaret = t.Dict(
    {
        t.Key("start_date"): parse_time,
        t.Key("end_date"): parse_time,
        t.Key("actual"): t.Float | t.Null,
        t.Key("predicted"): t.Float | t.Null,
        t.Key("frequency"): Int | t.Null,
    }
).ignore_extra("*")

_forecast_vs_actual_plots_bin_trafaret = t.Dict(
    {
        t.Key("start_date"): parse_time,
        t.Key("end_date"): parse_time,
        t.Key("actual"): t.Float | t.Null,
        t.Key("error"): t.Float | t.Null,
        t.Key("normalized_error"): t.Float | t.Null,
        t.Key("forecasts"): t.List(t.Float | t.Null),
        t.Key("frequency"): Int | t.Null,
    }
).ignore_extra("*")

_anomaly_over_time_plots_bin_trafaret = t.Dict(
    {
        t.Key("start_date"): parse_time,
        t.Key("end_date"): parse_time,
        t.Key("predicted"): t.Float | t.Null,
        t.Key("frequency"): Int | t.Null,
    }
).ignore_extra("*")

_datetime_trend_plots_preview_bin_trafaret = t.Dict(
    {
        t.Key("start_date"): parse_time,
        t.Key("end_date"): parse_time,
        t.Key("actual"): t.Float | t.Null,
        t.Key("predicted"): t.Float | t.Null,
    }
).ignore_extra("*")

_anomaly_over_time_plots_preview_bin_trafaret = t.Dict(
    {t.Key("start_date"): parse_time, t.Key("end_date"): parse_time}
).ignore_extra("*")


_calendar_event_trafaret = t.Dict(
    {t.Key("name"): String, t.Key("date"): parse_time, t.Key("series_id"): String | t.Null}
).ignore_extra("*")

_statistics_trafaret = t.Dict({t.Key("durbin_watson"): t.Float | t.Null}).ignore_extra("*")


class DatetimeTrendPlotsAPIObject(APIObject):
    @classmethod
    def from_server_data(cls, data):
        """
        Instantiate an object of this class using the data directly from the server,
        meaning that the keys may have the wrong camel casing.

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        """
        return cls.from_data(from_api(data, keep_null_keys=True))


class DatetimeTrendPlotsMetadataObject(DatetimeTrendPlotsAPIObject):
    def _get_status(self, backtest=0, source=SOURCE_TYPE.VALIDATION):
        try:
            if backtest == DATA_SUBSET.HOLDOUT:
                return self.holdout_statuses[source]
            else:
                return self.backtest_statuses[backtest][source]
        except (TypeError, KeyError, IndexError):
            return None


class AccuracyOverTimePlotsMetadata(DatetimeTrendPlotsMetadataObject):
    """
    Accuracy over Time metadata for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    forecast_distance: int or None
        The forecast distance for which the metadata was retrieved. None for OTV projects.
    resolutions: list of string
        A list of ``datarobot.enums.DATETIME_TREND_PLOTS_RESOLUTION``, which represents
        available time resolutions for which plots can be retrieved.
    backtest_metadata: list of dict
        List of backtest metadata dicts.
        The list index of metadata dict is the backtest index.
        See backtest/holdout metadata info in `Notes` for more details.
    holdout_metadata: dict
        Holdout metadata dict. See backtest/holdout metadata info in `Notes` for more details.
    backtest_statuses: list of dict
        List of backtest statuses dict. The list index of status dict is the backtest index.
        See backtest/holdout status info in `Notes` for more details.
    holdout_statuses: dict
        Holdout status dict. See backtest/holdout status info in `Notes` for more details.

    Notes
    -----

    Backtest/holdout status is a dict containing the following:

    * training: string
        Status backtest/holdout training. One of ``datarobot.enums.DATETIME_TREND_PLOTS_STATUS``
    * validation: string
        Status backtest/holdout validation. One of ``datarobot.enums.DATETIME_TREND_PLOTS_STATUS``

    Backtest/holdout metadata is a dict containing the following:

    * training: dict
        Start and end dates for the backtest/holdout training.
    * validation: dict
        Start and end dates for the backtest/holdout validation.

    Each dict in the `training` and `validation` in backtest/holdout metadata is structured like:

    * start_date: datetime.datetime or None
        The datetime of the start of the chart data (inclusive). None if chart data is not computed.
    * end_date: datetime.datetime or None
        The datetime of the end of the chart data (exclusive). None if chart data is not computed.
    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("forecast_distance"): Int | t.Null,
            t.Key("resolutions"): t.List(t.Enum(*DATETIME_TREND_PLOTS_RESOLUTION.ALL)),
            t.Key("backtest_metadata"): t.List(_backtest_holdout_metadata_trafaret),
            t.Key("holdout_metadata"): _backtest_holdout_metadata_trafaret,
            t.Key("backtest_statuses"): t.List(_accuracy_anomaly_over_time_plots_status_trafaret),
            t.Key("holdout_statuses"): _accuracy_anomaly_over_time_plots_status_trafaret,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id,
        model_id,
        forecast_distance,
        resolutions,
        backtest_metadata,
        holdout_metadata,
        backtest_statuses,
        holdout_statuses,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.forecast_distance = forecast_distance
        self.resolutions = resolutions
        self.backtest_metadata = backtest_metadata
        self.holdout_metadata = holdout_metadata
        self.backtest_statuses = backtest_statuses
        self.holdout_statuses = holdout_statuses

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={}, forecast_distance={})".format(
                self.__class__.__name__, self.project_id, self.model_id, self.forecast_distance,
            )
        )


class AccuracyOverTimePlot(DatetimeTrendPlotsAPIObject):
    """
    Accuracy over Time plot for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    resolution: string
        The resolution that is used for binning.
        One of ``datarobot.enums.DATETIME_TREND_PLOTS_RESOLUTION``
    start_date: datetime.datetime
        The datetime of the start of the chart data (inclusive).
    end_date: datetime.datetime
        The datetime of the end of the chart data (exclusive).
    bins: list of dict
        List of plot bins. See bin info in `Notes` for more details.
    statistics: dict
        Statistics for plot. See statistics info in `Notes` for more details.
    calendar_events: list of dict
        List of calendar events for the plot. See calendar events info in `Notes` for more details.

    Notes
    -----

    Bin is a dict containing the following:

    * start_date: datetime.datetime
        The datetime of the start of the bin (inclusive).
    * end_date: datetime.datetime
        The datetime of the end of the bin (exclusive).
    * actual: float or None
        Average actual value of the target in the bin. None if there are no entries in the bin.
    * predicted: float or None
        Average prediction of the model in the bin. None if there are no entries in the bin.
    * frequency: int or None
        Indicates number of values averaged in bin.

    Statistics is a dict containing the following:

    * durbin_watson: float or None
        The Durbin-Watson statistic for the chart data.
        Value is between 0 and 4. Durbin-Watson statistic
        is a test statistic used to detect the presence of
        autocorrelation at lag 1 in the residuals (prediction errors)
        from a regression analysis. More info
        https://wikipedia.org/wiki/Durbin%E2%80%93Watson_statistic

    Calendar event is a dict containing the following:

    * name: string
        Name of the calendar event.
    * date: datetime
        Date of the calendar event.
    * series_id: string or None
        The series ID for the event. If this event does not specify a series ID,
        then this will be None, indicating that the event applies to all series.
    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("start_date"): parse_time,
            t.Key("end_date"): parse_time,
            t.Key("resolution"): t.Enum(*DATETIME_TREND_PLOTS_RESOLUTION.ALL),
            t.Key("bins"): t.List(_accuracy_over_time_plots_bin_trafaret),
            t.Key("statistics"): _statistics_trafaret,
            t.Key("calendar_events"): t.List(_calendar_event_trafaret),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id,
        model_id,
        start_date,
        end_date,
        resolution,
        bins,
        statistics,
        calendar_events,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.start_date = start_date
        self.end_date = end_date
        self.resolution = resolution
        self.bins = bins
        self.statistics = statistics
        self.calendar_events = calendar_events

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={}, start_date={}, end_date={})".format(
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                datetime_to_string(self.start_date, ensure_rfc_3339=True),
                datetime_to_string(self.end_date, ensure_rfc_3339=True),
            )
        )


class AccuracyOverTimePlotPreview(DatetimeTrendPlotsAPIObject):
    """
    Accuracy over Time plot preview for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    start_date: datetime.datetime
        The datetime of the start of the chart data (inclusive).
    end_date: datetime.datetime
        The datetime of the end of the chart data (exclusive).
    bins: list of dict
        List of plot bins. See bin info in `Notes` for more details.

    Notes
    -----

    Bin is a dict containing the following:

    * start_date: datetime.datetime
        The datetime of the start of the bin (inclusive).
    * end_date: datetime.datetime
        The datetime of the end of the bin (exclusive).
    * actual: float or None
        Average actual value of the target in the bin. None if there are no entries in the bin.
    * predicted: float or None
        Average prediction of the model in the bin. None if there are no entries in the bin.

    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("start_date"): parse_time,
            t.Key("end_date"): parse_time,
            t.Key("bins"): t.List(_datetime_trend_plots_preview_bin_trafaret),
        }
    ).ignore_extra("*")

    def __init__(self, project_id, model_id, start_date, end_date, bins):
        self.project_id = project_id
        self.model_id = model_id
        self.start_date = start_date
        self.end_date = end_date
        self.bins = bins

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={})".format(
                self.__class__.__name__, self.project_id, self.model_id
            )
        )


class ForecastVsActualPlotsMetadata(DatetimeTrendPlotsMetadataObject):
    """
    Forecast vs Actual plots metadata for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    resolutions: list of string
        A list of ``datarobot.enums.DATETIME_TREND_PLOTS_RESOLUTION``, which represents
        available time resolutions for which plots can be retrieved.
    backtest_metadata: list of dict
        List of backtest metadata dicts.
        The list index of metadata dict is the backtest index.
        See backtest/holdout metadata info in `Notes` for more details.
    holdout_metadata: dict
        Holdout metadata dict. See backtest/holdout metadata info in `Notes` for more details.
    backtest_statuses: list of dict
        List of backtest statuses dict. The list index of status dict is the backtest index.
        See backtest/holdout status info in `Notes` for more details.
    holdout_statuses: dict
        Holdout status dict. See backtest/holdout status info in `Notes` for more details.

    Notes
    -----

    Backtest/holdout status is a dict containing the following:

    * training: dict
        Dict containing each of ``datarobot.enums.DATETIME_TREND_PLOTS_STATUS`` as dict key,
        and list of forecast distances for particular status as dict value.

    * validation: dict
        Dict containing each of ``datarobot.enums.DATETIME_TREND_PLOTS_STATUS`` as dict key,
        and list of forecast distances for particular status as dict value.

    Backtest/holdout metadata is a dict containing the following:

    * training: dict
        Start and end dates for the backtest/holdout training.
    * validation: dict
        Start and end dates for the backtest/holdout validation.

    Each dict in the `training` and `validation` in backtest/holdout metadata is structured like:

    * start_date: datetime.datetime or None
        The datetime of the start of the chart data (inclusive). None if chart data is not computed.
    * end_date: datetime.datetime or None
        The datetime of the end of the chart data (exclusive). None if chart data is not computed.
    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("resolutions"): t.List(t.Enum(*DATETIME_TREND_PLOTS_RESOLUTION.ALL)),
            t.Key("backtest_metadata"): t.List(_backtest_holdout_metadata_trafaret),
            t.Key("holdout_metadata"): _backtest_holdout_metadata_trafaret,
            t.Key("backtest_statuses"): t.List(_forecast_vs_actual_status_trafaret),
            t.Key("holdout_statuses"): _forecast_vs_actual_status_trafaret,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id,
        model_id,
        resolutions,
        backtest_metadata,
        holdout_metadata,
        backtest_statuses,
        holdout_statuses,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.resolutions = resolutions
        self.backtest_metadata = backtest_metadata
        self.holdout_metadata = holdout_metadata
        self.backtest_statuses = backtest_statuses
        self.holdout_statuses = holdout_statuses

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={})".format(
                self.__class__.__name__, self.project_id, self.model_id,
            )
        )


class ForecastVsActualPlot(DatetimeTrendPlotsAPIObject):
    """
    Forecast vs Actual plot for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    forecast_distances: list of int
        A list of forecast distances that were retrieved.
    resolution: string
        The resolution that is used for binning.
        One of ``datarobot.enums.DATETIME_TREND_PLOTS_RESOLUTION``
    start_date: datetime.datetime
        The datetime of the start of the chart data (inclusive).
    end_date: datetime.datetime
        The datetime of the end of the chart data (exclusive).
    bins: list of dict
        List of plot bins. See bin info in `Notes` for more details.
    calendar_events: list of dict
        List of calendar events for the plot. See calendar events info in `Notes` for more details.

    Notes
    -----

    Bin is a dict containing the following:

    * start_date: datetime.datetime
        The datetime of the start of the bin (inclusive).
    * end_date: datetime.datetime
        The datetime of the end of the bin (exclusive).
    * actual: float or None
        Average actual value of the target in the bin. None if there are no entries in the bin.
    * forecasts: list of float
        A list of average forecasts for the model for each forecast distance.
        Empty if there are no forecasts in the bin.
        Each index in the `forecasts` list maps to `forecastDistances` list index.
    * error: float or None
        Average absolute residual value of the bin.
        None if there are no entries in the bin.
    * normalized_error: float or None
        Normalized average absolute residual value of the bin.
        None if there are no entries in the bin.
    * frequency: int or None
        Indicates number of values averaged in bin.

    Calendar event is a dict containing the following:

    * name: string
        Name of the calendar event.
    * date: datetime
        Date of the calendar event.
    * series_id: string or None
        The series ID for the event. If this event does not specify a series ID,
        then this will be None, indicating that the event applies to all series.
    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("forecast_distances"): t.List(Int),
            t.Key("start_date"): parse_time,
            t.Key("end_date"): parse_time,
            t.Key("resolution"): t.Enum(*DATETIME_TREND_PLOTS_RESOLUTION.ALL),
            t.Key("bins"): t.List(_forecast_vs_actual_plots_bin_trafaret),
            t.Key("calendar_events"): t.List(_calendar_event_trafaret),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id,
        model_id,
        forecast_distances,
        start_date,
        end_date,
        resolution,
        bins,
        calendar_events,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.forecast_distances = forecast_distances
        self.start_date = start_date
        self.end_date = end_date
        self.resolution = resolution
        self.bins = bins
        self.calendar_events = calendar_events

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={}, start_date={}, end_date={})".format(
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                datetime_to_string(self.start_date, ensure_rfc_3339=True),
                datetime_to_string(self.end_date, ensure_rfc_3339=True),
            )
        )


class ForecastVsActualPlotPreview(DatetimeTrendPlotsAPIObject):
    """
    Forecast vs Actual plot preview for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    start_date: datetime.datetime
        The datetime of the start of the chart data (inclusive).
    end_date: datetime.datetime
        The datetime of the end of the chart data (exclusive).
    bins: list of dict
        List of plot bins. See bin info in `Notes` for more details.

    Notes
    -----

    Bin is a dict containing the following:

    * start_date: datetime.datetime
        The datetime of the start of the bin (inclusive).
    * end_date: datetime.datetime
        The datetime of the end of the bin (exclusive).
    * actual: float or None
        Average actual value of the target in the bin. None if there are no entries in the bin.
    * predicted: float or None
        Average prediction of the model in the bin. None if there are no entries in the bin.

    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("start_date"): parse_time,
            t.Key("end_date"): parse_time,
            t.Key("bins"): t.List(_datetime_trend_plots_preview_bin_trafaret),
        }
    ).ignore_extra("*")

    def __init__(self, project_id, model_id, start_date, end_date, bins):
        self.project_id = project_id
        self.model_id = model_id
        self.start_date = start_date
        self.end_date = end_date
        self.bins = bins

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={})".format(
                self.__class__.__name__, self.project_id, self.model_id
            )
        )


class AnomalyOverTimePlotsMetadata(DatetimeTrendPlotsMetadataObject):
    """
    Anomaly over Time metadata for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    resolutions: list of string
        A list of ``datarobot.enums.DATETIME_TREND_PLOTS_RESOLUTION``, which represents
        available time resolutions for which plots can be retrieved.
    backtest_metadata: list of dict
        List of backtest metadata dicts.
        The list index of metadata dict is the backtest index.
        See backtest/holdout metadata info in `Notes` for more details.
    holdout_metadata: dict
        Holdout metadata dict. See backtest/holdout metadata info in `Notes` for more details.
    backtest_statuses: list of dict
        List of backtest statuses dict. The list index of status dict is the backtest index.
        See backtest/holdout status info in `Notes` for more details.
    holdout_statuses: dict
        Holdout status dict. See backtest/holdout status info in `Notes` for more details.

    Notes
    -----

    Backtest/holdout status is a dict containing the following:

    * training: string
        Status backtest/holdout training. One of ``datarobot.enums.DATETIME_TREND_PLOTS_STATUS``
    * validation: string
        Status backtest/holdout validation. One of ``datarobot.enums.DATETIME_TREND_PLOTS_STATUS``

    Backtest/holdout metadata is a dict containing the following:

    * training: dict
        Start and end dates for the backtest/holdout training.
    * validation: dict
        Start and end dates for the backtest/holdout validation.

    Each dict in the `training` and `validation` in backtest/holdout metadata is structured like:

    * start_date: datetime.datetime or None
        The datetime of the start of the chart data (inclusive). None if chart data is not computed.
    * end_date: datetime.datetime or None
        The datetime of the end of the chart data (exclusive). None if chart data is not computed.
    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("resolutions"): t.List(t.Enum(*DATETIME_TREND_PLOTS_RESOLUTION.ALL)),
            t.Key("backtest_metadata"): t.List(_backtest_holdout_metadata_trafaret),
            t.Key("holdout_metadata"): _backtest_holdout_metadata_trafaret,
            t.Key("backtest_statuses"): t.List(_accuracy_anomaly_over_time_plots_status_trafaret),
            t.Key("holdout_statuses"): _accuracy_anomaly_over_time_plots_status_trafaret,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id,
        model_id,
        resolutions,
        backtest_metadata,
        holdout_metadata,
        backtest_statuses,
        holdout_statuses,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.resolutions = resolutions
        self.backtest_metadata = backtest_metadata
        self.holdout_metadata = holdout_metadata
        self.backtest_statuses = backtest_statuses
        self.holdout_statuses = holdout_statuses

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={})".format(
                self.__class__.__name__, self.project_id, self.model_id
            )
        )


class AnomalyOverTimePlot(DatetimeTrendPlotsAPIObject):
    """
    Anomaly over Time plot for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    resolution: string
        The resolution that is used for binning.
        One of ``datarobot.enums.DATETIME_TREND_PLOTS_RESOLUTION``
    start_date: datetime.datetime
        The datetime of the start of the chart data (inclusive).
    end_date: datetime.datetime
        The datetime of the end of the chart data (exclusive).
    bins: list of dict
        List of plot bins. See bin info in `Notes` for more details.
    calendar_events: list of dict
        List of calendar events for the plot. See calendar events info in `Notes` for more details.

    Notes
    -----

    Bin is a dict containing the following:

    * start_date: datetime.datetime
        The datetime of the start of the bin (inclusive).
    * end_date: datetime.datetime
        The datetime of the end of the bin (exclusive).
    * predicted: float or None
        Average prediction of the model in the bin. None if there are no entries in the bin.
    * frequency: int or None
        Indicates number of values averaged in bin.

    Calendar event is a dict containing the following:

    * name: string
        Name of the calendar event.
    * date: datetime
        Date of the calendar event.
    * series_id: string or None
        The series ID for the event. If this event does not specify a series ID,
        then this will be None, indicating that the event applies to all series.
    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("start_date"): parse_time,
            t.Key("end_date"): parse_time,
            t.Key("resolution"): t.Enum(*DATETIME_TREND_PLOTS_RESOLUTION.ALL),
            t.Key("bins"): t.List(_anomaly_over_time_plots_bin_trafaret),
            t.Key("calendar_events"): t.List(_calendar_event_trafaret),
        }
    ).ignore_extra("*")

    def __init__(
        self, project_id, model_id, start_date, end_date, resolution, bins, calendar_events,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.start_date = start_date
        self.end_date = end_date
        self.resolution = resolution
        self.bins = bins
        self.calendar_events = calendar_events

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={}, start_date={}, end_date={})".format(
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                datetime_to_string(self.start_date, ensure_rfc_3339=True),
                datetime_to_string(self.end_date, ensure_rfc_3339=True),
            )
        )


class AnomalyOverTimePlotPreview(DatetimeTrendPlotsAPIObject):
    """
    Anomaly over Time plot preview for datetime model.

    .. versionadded:: v2.25

    Attributes
    ----------
    project_id: string
        The project ID.
    model_id: string
        The model ID.
    prediction_threshold: float
        Only bins with predictions exceeding
        this threshold are returned in the response.
    start_date: datetime.datetime
        The datetime of the start of the chart data (inclusive).
    end_date: datetime.datetime
        The datetime of the end of the chart data (exclusive).
    bins: list of dict
        List of plot bins. See bin info in `Notes` for more details.

    Notes
    -----

    Bin is a dict containing the following:

    * start_date: datetime.datetime
        The datetime of the start of the bin (inclusive).
    * end_date: datetime.datetime
        The datetime of the end of the bin (exclusive).

    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("prediction_threshold"): t.Float,
            t.Key("start_date"): parse_time,
            t.Key("end_date"): parse_time,
            t.Key("bins"): t.List(_anomaly_over_time_plots_preview_bin_trafaret),
        }
    ).ignore_extra("*")

    def __init__(self, project_id, model_id, prediction_threshold, start_date, end_date, bins):
        self.project_id = project_id
        self.model_id = model_id
        self.prediction_threshold = prediction_threshold
        self.start_date = start_date
        self.end_date = end_date
        self.bins = bins

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(project_id={}, model_id={})".format(
                self.__class__.__name__, self.project_id, self.model_id
            )
        )
