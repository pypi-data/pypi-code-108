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
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject

from ..enums import SERVICE_STAT_METRIC
from ..helpers.deployment_monitoring import DeploymentQueryBuilderMixin
from ..utils import encode_utf8_if_py2, from_api


class ServiceStats(APIObject, DeploymentQueryBuilderMixin):
    """Deployment service stats information.

    Attributes
    ----------
    model_id : str
        the model used to retrieve service stats metrics
    period : dict
        the time period used to retrieve service stats metrics
    metrics : dict
        the service stats metrics
    """

    _path = "deployments/{}/serviceStats/"
    _period = t.Dict(
        {
            t.Key("start"): t.String >> (lambda s: dateutil.parser.parse(s)),
            t.Key("end"): t.String >> (lambda s: dateutil.parser.parse(s)),
        }
    )
    _converter = t.Dict(
        {
            t.Key("period"): _period,
            t.Key("metrics"): t.Dict(
                {
                    t.Key(SERVICE_STAT_METRIC.TOTAL_PREDICTIONS): t.Int(),
                    t.Key(SERVICE_STAT_METRIC.TOTAL_REQUESTS, optional=True): t.Int(),
                    t.Key(SERVICE_STAT_METRIC.SLOW_REQUESTS, optional=True): t.Int(),
                    t.Key(SERVICE_STAT_METRIC.EXECUTION_TIME, optional=True): t.Float() | t.Null(),
                    t.Key(SERVICE_STAT_METRIC.RESPONSE_TIME, optional=True): t.Float() | t.Null(),
                    t.Key(SERVICE_STAT_METRIC.USER_ERROR_RATE, optional=True): t.Float(),
                    t.Key(SERVICE_STAT_METRIC.SERVER_ERROR_RATE, optional=True): t.Float(),
                    t.Key(SERVICE_STAT_METRIC.NUM_CONSUMERS, optional=True): t.Int(),
                    t.Key(SERVICE_STAT_METRIC.CACHE_HIT_RATIO, optional=True): t.Float(),
                    t.Key(SERVICE_STAT_METRIC.MEDIAN_LOAD, optional=True): t.Float(),
                    t.Key(SERVICE_STAT_METRIC.PEAK_LOAD, optional=True): t.Float(),
                }
            ).allow_extra("*", trafaret=t.Or(t.Int(), t.Float(), t.Null())),
            t.Key("model_id"): t.String() | t.Null,
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
        return self.metrics.get(item)

    @classmethod
    def get(
        cls,
        deployment_id,
        model_id=None,
        start_time=None,
        end_time=None,
        execution_time_quantile=None,
        response_time_quantile=None,
        slow_requests_threshold=None,
    ):
        """Retrieve value of service stat metrics over a certain time period.

        .. versionadded:: v2.18

        Parameters
        ----------
        deployment_id : str
            the id of the deployment
        model_id : str, optional
            the id of the model
        start_time : datetime, optional
            start of the time period
        end_time : datetime, optional
            end of the time period
        execution_time_quantile : float, optional
            quantile for `executionTime`, defaults to 0.5
        response_time_quantile : float, optional
            quantile for `responseTime`, defaults to 0.5
        slow_requests_threshold : float, optional
            threshold for `slowRequests`, defaults to 1000

        Returns
        -------
        service_stats : ServiceStats
            the queried service stats metrics
        """

        path = cls._path.format(deployment_id)
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "model_id": model_id,
            "execution_time_quantile": execution_time_quantile,
            "response_time_quantile": response_time_quantile,
            "slow_requests_threshold": slow_requests_threshold,
        }
        params = cls._build_query_params(**params)
        data = cls._client.get(path, params=params).json()

        # we don't want to convert keys of the metrics object
        metrics = data.pop("metrics")

        data = from_api(data, keep_null_keys=True)
        data["metrics"] = metrics
        return cls.from_data(data)


class ServiceStatsOverTime(APIObject, DeploymentQueryBuilderMixin):
    """Deployment service stats over time information.

    Attributes
    ----------
    model_id : str
        the model used to retrieve accuracy metric
    metric : str
        the service stat metric being retrieved
    buckets : dict
        how the service stat metric changes over time
    summary : dict
        summary for the service stat metric
    """

    _path = "deployments/{}/serviceStatsOverTime/"
    _period = t.Dict(
        {
            t.Key("start"): String >> (lambda s: dateutil.parser.parse(s)),
            t.Key("end"): String >> (lambda s: dateutil.parser.parse(s)),
        }
    )
    _bucket = t.Dict(
        {t.Key("period"): _period | t.Null, t.Key("value"): Int | t.Float | t.Null}
    ).allow_extra("*")
    _converter = t.Dict(
        {
            t.Key("buckets"): t.List(_bucket),
            t.Key("summary"): _bucket,
            t.Key("metric"): String(),
            t.Key("model_id"): String() | t.Null,
        }
    ).allow_extra("*")

    def __init__(self, buckets=None, summary=None, metric=None, model_id=None):
        self.buckets = buckets
        self.summary = summary
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
        quantile=None,
        threshold=None,
    ):
        """Retrieve information about how a service stat metric changes over a certain time period.

        .. versionadded:: v2.18

        Parameters
        ----------
        deployment_id : str
            the id of the deployment
        metric : SERVICE_STAT_METRIC, optional
            the service stat metric to retrieve
        model_id : str, optional
            the id of the model
        start_time : datetime, optional
            start of the time period
        end_time : datetime, optional
            end of the time period
        bucket_size : str, optional
            time duration of a bucket, in ISO 8601 time duration format
        quantile : float, optional
            quantile for 'executionTime' or 'responseTime', ignored when querying other metrics
        threshold : int, optional
            threshold for 'slowQueries', ignored when querying other metrics

        Returns
        -------
        service_stats_over_time : ServiceStatsOverTime
            the queried service stat over time information
        """

        path = cls._path.format(deployment_id)
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "model_id": model_id,
            "metric": metric,
            "bucket_size": bucket_size,
            "quantile": quantile,
            "threshold": threshold,
        }
        params = cls._build_query_params(**params)
        data = cls._client.get(path, params=params).json()
        case_converted = from_api(data, keep_null_keys=True)
        return cls.from_data(case_converted)

    @property
    def bucket_values(self):
        """The metric value for all time buckets, keyed by start time of the bucket.

        Returns
        -------
        bucket_values: OrderedDict
        """

        values = [(bucket["period"]["start"], bucket["value"]) for bucket in self.buckets]
        return OrderedDict(values)
