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
from collections import OrderedDict

import dateutil
import pandas as pd
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject

from ..enums import ACCURACY_METRIC
from ..helpers.deployment_monitoring import DeploymentQueryBuilderMixin
from ..utils import encode_utf8_if_py2, from_api


class Accuracy(APIObject, DeploymentQueryBuilderMixin):
    """Deployment accuracy information.

    Attributes
    ----------
    model_id : str
        the model used to retrieve accuracy metrics
    period : dict
        the time period used to retrieve accuracy metrics
    metrics : dict
        the accuracy metrics
    """

    _path = "deployments/{}/accuracy/"
    _period = t.Dict(
        {
            t.Key("start"): String >> (lambda s: dateutil.parser.parse(s)),
            t.Key("end"): String >> (lambda s: dateutil.parser.parse(s)),
        }
    )
    _metric = t.Dict(
        {
            t.Key("value", optional=True): t.Float | t.Null,
            t.Key("baseline_value", optional=True): t.Float | t.Null,
            t.Key("percent_change", optional=True): t.Float | t.Null,
        }
    ).allow_extra("*")
    _converter = t.Dict(
        {
            t.Key("period"): _period,
            t.Key("metrics"): t.Mapping(t.Enum(*ACCURACY_METRIC.ALL), _metric),
            t.Key("model_id"): String() | t.Null,
        }
    ).allow_extra("*")

    def __init__(self, period=None, metrics=None, model_id=None):
        self.period = period or {}
        self.metrics = metrics or {}
        self.model_id = model_id

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}({} | {} - {})".format(
                self.__class__.__name__,
                self.model_id,
                self.period.get("start"),
                self.period.get("end"),
            )
        )

    def __getitem__(self, item):
        return self.metrics.get(item, {}).get("value")

    @classmethod
    def get(cls, deployment_id, model_id=None, start_time=None, end_time=None):
        """Retrieve values of accuracy metrics over a certain time period.

        .. versionadded:: v2.18

        Parameters
        ----------
        deployment_id : str
            the id of the deployment
        model_id : str
            the id of the model
        start_time : datetime
            start of the time period
        end_time : datetime
            end of the time period

        Returns
        -------
        accuracy : Accuracy
            the queried accuracy metrics information

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment, Accuracy
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            accuracy = Accuracy.get(deployment.id)
            accuracy.period['end']
            >>>'2019-08-01 00:00:00+00:00'
            accuracy.metric['LogLoss']['value']
            >>>0.7533
            accuracy.metric_values['LogLoss']
            >>>0.7533
        """

        path = cls._path.format(deployment_id)
        params = cls._build_query_params(
            start_time=start_time, end_time=end_time, model_id=model_id
        )
        data = cls._client.get(path, params=params).json()

        # we don't want to convert keys of the metrics object
        metrics = data.pop("metrics")
        for metric, value in metrics.items():
            metrics[metric] = from_api(value, keep_null_keys=True)

        data = from_api(data, keep_null_keys=True)
        data["metrics"] = metrics
        return cls.from_data(data)

    @property
    def metric_values(self):
        """The value for all metrics, keyed by metric name.

        Returns
        -------
        metric_values: OrderedDict
        """

        return {name: value.get("value") for name, value in self.metrics.items()}

    @property
    def metric_baselines(self):
        """The baseline value for all metrics, keyed by metric name.

        Returns
        -------
        metric_baselines: OrderedDict
        """

        return {name: value.get("baseline_value") for name, value in self.metrics.items()}

    @property
    def percent_changes(self):
        """The percent change of value over baseline for all metrics, keyed by metric name.

        Returns
        -------
        percent_changes: OrderedDict
        """

        return {name: value.get("percent_change") for name, value in self.metrics.items()}


class AccuracyOverTime(APIObject, DeploymentQueryBuilderMixin):
    """Deployment accuracy over time information.

    Attributes
    ----------
    model_id : str
        the model used to retrieve accuracy metric
    metric : str
        the accuracy metric being retrieved
    buckets : dict
        how the accuracy metric changes over time
    summary : dict
        summary for the accuracy metric
    baseline : dict
        baseline for the accuracy metric
    """

    _path = "deployments/{}/accuracyOverTime/"
    _period = t.Dict(
        {
            t.Key("start"): String >> (lambda s: dateutil.parser.parse(s)),
            t.Key("end"): String >> (lambda s: dateutil.parser.parse(s)),
        }
    )
    _bucket = t.Dict(
        {
            t.Key("period"): _period | t.Null,
            t.Key("value"): t.Float | t.Null,
            t.Key("sample_size"): Int | t.Null,
        }
    ).allow_extra("*")
    _converter = t.Dict(
        {
            t.Key("buckets"): t.List(_bucket),
            t.Key("summary"): _bucket,
            t.Key("baseline"): _bucket,
            t.Key("metric"): String(),
            t.Key("model_id"): String() | t.Null,
        }
    ).allow_extra("*")

    def __init__(self, buckets=None, summary=None, baseline=None, metric=None, model_id=None):
        self.buckets = buckets
        self.summary = summary
        self.baseline = baseline
        self.metric = metric
        self.model_id = model_id

    def __repr__(self):
        period = self.summary.get("period") or {}
        return encode_utf8_if_py2(
            u"{}({} | {} | {} - {})".format(
                self.__class__.__name__,
                self.model_id,
                self.metric,
                period.get("start"),
                period.get("end"),
            )
        )

    @classmethod
    def get(
        cls,
        deployment_id,
        metric=None,
        model_id=None,
        start_time=None,
        end_time=None,
        bucket_size=None,
    ):
        """Retrieve information about how an accuracy metric changes over a certain time period.

        .. versionadded:: v2.18

        Parameters
        ----------
        deployment_id : str
            the id of the deployment
        metric : ACCURACY_METRIC
            the accuracy metric to retrieve
        model_id : str
            the id of the model
        start_time : datetime
            start of the time period
        end_time : datetime
            end of the time period
        bucket_size : str
            time duration of a bucket, in ISO 8601 time duration format

        Returns
        -------
        accuracy_over_time : AccuracyOverTime
            the queried accuracy metric over time information

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment, AccuracyOverTime
            from datarobot.enums import ACCURACY_METRICS
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            accuracy_over_time = AccuracyOverTime.get(deployment.id, metric=ACCURACY_METRIC.LOGLOSS)
            accuracy_over_time.metric
            >>>'LogLoss'
            accuracy_over_time.metric_values
            >>>{datetime.datetime(2019, 8, 1): 0.73, datetime.datetime(2019, 8, 2): 0.55}
        """

        path = cls._path.format(deployment_id)
        params = cls._build_query_params(
            start_time=start_time,
            end_time=end_time,
            model_id=model_id,
            metric=metric,
            bucket_size=bucket_size,
        )
        data = cls._client.get(path, params=params).json()
        case_converted = from_api(data, keep_null_keys=True)
        return cls.from_data(case_converted)

    @classmethod
    def get_as_dataframe(
        cls, deployment_id, metrics, model_id=None, start_time=None, end_time=None, bucket_size=None
    ):
        """Retrieve information about how a list of accuracy metrics change over
        a certain time period as pandas DataFrame.

        In the returned DataFrame, the columns corresponds to the metrics being retrieved;
        the rows are labeled with the start time of each bucket.

        Parameters
        ----------
        deployment_id : str
            the id of the deployment
        metrics : [ACCURACY_METRIC]
            the accuracy metrics to retrieve
        model_id : str
            the id of the model
        start_time : datetime
            start of the time period
        end_time : datetime
            end of the time period
        bucket_size : str
            time duration of a bucket, in ISO 8601 time duration format

        Returns
        -------
        accuracy_over_time: pd.DataFrame
        """

        if metrics is None:
            metrics = []
        metric_names = []
        metric_dataframes = []
        for metric_name in metrics:
            fetched = AccuracyOverTime.get(
                deployment_id,
                model_id=model_id,
                metric=metric_name,
                start_time=start_time,
                end_time=end_time,
                bucket_size=bucket_size,
            )
            dataframe = pd.DataFrame.from_dict(fetched.bucket_values, orient="index")
            metric_names.append(fetched.metric)
            metric_dataframes.append(dataframe)
        combined = pd.concat(metric_dataframes, axis="columns")
        combined.columns = metric_names
        return combined

    @property
    def bucket_values(self):
        """The metric value for all time buckets, keyed by start time of the bucket.

        Returns
        -------
        bucket_values: OrderedDict
        """

        values = [(bucket["period"]["start"], bucket["value"]) for bucket in self.buckets]
        return OrderedDict(values)

    @property
    def bucket_sample_sizes(self):
        """The sample size for all time buckets, keyed by start time of the bucket.

        Returns
        -------
        bucket_sample_sizes: OrderedDict
        """

        values = [(bucket["period"]["start"], bucket["sample_size"]) for bucket in self.buckets]
        return OrderedDict(values)
