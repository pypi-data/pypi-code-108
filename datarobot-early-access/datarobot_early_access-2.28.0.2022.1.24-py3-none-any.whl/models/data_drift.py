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
import dateutil
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject

from ..enums import DATA_DRIFT_METRIC
from ..helpers.deployment_monitoring import DeploymentQueryBuilderMixin
from ..utils import encode_utf8_if_py2, from_api


class TargetDrift(APIObject, DeploymentQueryBuilderMixin):
    """Deployment target drift information.

    Attributes
    ----------
    model_id : str
        the model used to retrieve target drift metric
    period : dict
        the time period used to retrieve target drift metric
    metric : str
        the data drift metric
    target_name : str
        name of the target
    drift_score : float
        target drift score
    sample_size : int
        count of data points for comparison
    baseline_sample_size : int
        count of data points for baseline
    """

    _path = "deployments/{}/targetDrift/"
    _period = t.Dict(
        {
            t.Key("start"): String >> (lambda s: dateutil.parser.parse(s)),
            t.Key("end"): String >> (lambda s: dateutil.parser.parse(s)),
        }
    )
    _converter = t.Dict(
        {
            t.Key("period"): _period,
            t.Key("metric"): t.Enum(*DATA_DRIFT_METRIC.ALL) | t.Null,
            t.Key("model_id"): String() | t.Null,
            t.Key("target_name"): String() | t.Null,
            t.Key("drift_score"): t.Float() | t.Null,
            t.Key("sample_size"): Int() | t.Null,
            t.Key("baseline_sample_size"): Int() | t.Null,
        }
    ).allow_extra("*")

    def __init__(
        self,
        period=None,
        metric=None,
        model_id=None,
        target_name=None,
        drift_score=None,
        sample_size=None,
        baseline_sample_size=None,
    ):
        self.period = period or {}
        self.metric = metric
        self.model_id = model_id
        self.target_name = target_name
        self.drift_score = drift_score
        self.sample_size = sample_size
        self.baseline_sample_size = baseline_sample_size

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}({} | {} | {} - {})".format(
                self.__class__.__name__,
                self.model_id,
                self.target_name,
                self.period.get("start"),
                self.period.get("end"),
            )
        )

    @classmethod
    def get(cls, deployment_id, model_id=None, start_time=None, end_time=None, metric=None):
        """Retrieve target drift information over a certain time period.

        .. versionadded:: v2.21

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
        metric : str
            (New in version v2.22) metric used to calculate the drift score

        Returns
        -------
        target_drift : TargetDrift
            the queried target drift information

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment, TargetDrift
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            target_drift = TargetDrift.get(deployment.id)
            target_drift.period['end']
            >>>'2019-08-01 00:00:00+00:00'
            target_drift.drift_score
            >>>0.03423
            accuracy.target_name
            >>>'readmitted'
        """

        path = cls._path.format(deployment_id)
        params = cls._build_query_params(
            start_time=start_time, end_time=end_time, model_id=model_id
        )
        if metric:
            params["metric"] = metric
        data = cls._client.get(path, params=params).json()
        data = from_api(data, keep_null_keys=True)
        return cls.from_data(data)


class FeatureDrift(APIObject, DeploymentQueryBuilderMixin):
    """Deployment feature drift information.

    Attributes
    ----------
    model_id : str
        the model used to retrieve feature drift metric
    period : dict
        the time period used to retrieve feature drift metric
    metric : str
        the data drift metric
    name : str
        name of the feature
    drift_score : float
        feature drift score
    sample_size : int
        count of data points for comparison
    baseline_sample_size : int
        count of data points for baseline
    """

    _path = "deployments/{}/featureDrift/"
    _period = t.Dict(
        {
            t.Key("start"): String >> (lambda s: dateutil.parser.parse(s)),
            t.Key("end"): String >> (lambda s: dateutil.parser.parse(s)),
        }
    )
    _converter = t.Dict(
        {
            t.Key("period"): _period,
            t.Key("metric"): t.Enum(*DATA_DRIFT_METRIC.ALL) | t.Null,
            t.Key("model_id"): String() | t.Null,
            t.Key("name"): String() | t.Null,
            t.Key("drift_score"): t.Float() | t.Null,
            t.Key("feature_impact"): t.Float() | t.Null,
            t.Key("sample_size"): Int() | t.Null,
            t.Key("baseline_sample_size"): Int() | t.Null,
        }
    ).allow_extra("*")

    def __init__(
        self,
        period=None,
        metric=None,
        model_id=None,
        name=None,
        drift_score=None,
        feature_impact=None,
        sample_size=None,
        baseline_sample_size=None,
    ):
        self.period = period or {}
        self.metric = metric
        self.model_id = model_id
        self.name = name
        self.drift_score = drift_score
        self.feature_impact = feature_impact
        self.sample_size = sample_size
        self.baseline_sample_size = baseline_sample_size

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}({} | {} | {} - {})".format(
                self.__class__.__name__,
                self.model_id,
                self.name,
                self.period.get("start"),
                self.period.get("end"),
            )
        )

    @classmethod
    def list(cls, deployment_id, model_id=None, start_time=None, end_time=None, metric=None):
        """Retrieve drift information for deployment's features over a certain time period.

        .. versionadded:: v2.21

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
        metric : str
            (New in version v2.22) metric used to calculate the drift score

        Returns
        -------
        feature_drift_data : [FeatureDrift]
            the queried feature drift information

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment, TargetDrift
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            feature_drift = FeatureDrift.list(deployment.id)[0]
            feature_drift.period
            >>>'2019-08-01 00:00:00+00:00'
            feature_drift.drift_score
            >>>0.252
            feature_drift.name
            >>>'age'
        """

        url = cls._path.format(deployment_id)
        params = cls._build_query_params(
            start_time=start_time, end_time=end_time, model_id=model_id
        )
        if metric:
            params["metric"] = metric
        response_json = cls._client.get(url, params=params).json()
        response_json = from_api(response_json, keep_null_keys=True)

        period = response_json.get("period", {})
        metric = response_json.get("metric")
        model_id = response_json.get("model_id")

        def _from_data_item(item):
            item["period"] = period
            item["metric"] = metric
            item["model_id"] = model_id
            return cls.from_data(item)

        data = []
        for item in response_json["data"]:
            data.append(_from_data_item(item))
        while response_json["next"] is not None:
            response_json = cls._client.get(response_json["next"]).json()
            response_json = from_api(response_json, keep_null_keys=True)
            for item in response_json["data"]:
                data.append(_from_data_item(item))

        return data
