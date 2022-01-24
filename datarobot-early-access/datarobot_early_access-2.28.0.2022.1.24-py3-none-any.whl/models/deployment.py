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
from collections import defaultdict
from datetime import datetime

import dateutil
import pandas as pd
import pytz
import trafaret as t

from datarobot._compat import String
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.models.custom_inference_image import CustomInferenceImage
from datarobot.models.custom_model_version import CustomModelVersion

from ..helpers.deployment_monitoring import DeploymentQueryBuilderMixin
from ..utils import deprecated, encode_utf8_if_py2, from_api, get_id_from_location
from ..utils.pagination import unpaginate
from ..utils.waiters import wait_for_async_resolution
from .accuracy import Accuracy, AccuracyOverTime
from .data_drift import FeatureDrift, TargetDrift
from .service_stats import ServiceStats, ServiceStatsOverTime


class Deployment(APIObject, DeploymentQueryBuilderMixin):
    """A deployment created from a DataRobot model.

    Attributes
    ----------
    id : str
        the id of the deployment
    label : str
        the label of the deployment
    description : str
        the description of the deployment
    default_prediction_server : dict
        information on the default prediction server of the deployment
    importance : str, optional
        deployment importance
    model : dict
        information on the model of the deployment
    capabilities : dict
        information on the capabilities of the deployment
    prediction_usage : dict
        information on the prediction usage of the deployment
    permissions : list
        (New in version v2.18) user's permissions on the deployment
    service_health : dict
        information on the service health of the deployment
    model_health : dict
        information on the model health of the deployment
    accuracy_health : dict
        information on the accuracy health of the deployment
    """

    _path = "deployments/"
    _default_prediction_server_converter = t.Dict(
        {
            t.Key("id", optional=True): String(allow_blank=True),
            t.Key("url", optional=True): String(allow_blank=True),
            t.Key("datarobot-key", optional=True): String(allow_blank=True),
        }
    ).allow_extra("*")
    _model_converter = t.Dict(
        {
            t.Key("id", optional=True): String(),
            t.Key("type", optional=True): String(allow_blank=True),
            t.Key("target_name", optional=True): String(allow_blank=True),
            t.Key("project_id", optional=True): String(allow_blank=True),
        }
    ).allow_extra("*")
    _capabilities = t.Dict(
        {
            t.Key("supports_drift_tracking", optional=True): t.Bool(),
            t.Key("supports_model_replacement", optional=True): t.Bool(),
        }
    ).allow_extra("*")
    _prediction_usage = t.Dict(
        {
            t.Key("daily_rates", optional=True): t.List(t.Float()),
            t.Key("last_timestamp", optional=True): String >> (lambda s: dateutil.parser.parse(s)),
        }
    ).allow_extra("*")
    _health = t.Dict(
        {
            t.Key("status", optional=True): String(allow_blank=True),
            t.Key("message", optional=True): String(allow_blank=True),
            t.Key("start_date", optional=True): String >> (lambda s: dateutil.parser.parse(s)),
            t.Key("end_date", optional=True): String >> (lambda s: dateutil.parser.parse(s)),
        }
    ).allow_extra("*")
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("label", optional=True): String(allow_blank=True),
            t.Key("description", optional=True): String(allow_blank=True) | t.Null(),
            t.Key("default_prediction_server", optional=True): _default_prediction_server_converter,
            t.Key("importance", optional=True): String() | t.Null(),
            t.Key("model", optional=True): _model_converter,
            t.Key("capabilities", optional=True): _capabilities,
            t.Key("prediction_usage", optional=True): _prediction_usage,
            t.Key("permissions", optional=True): t.List(String),
            t.Key("service_health", optional=True): _health,
            t.Key("model_health", optional=True): _health,
            t.Key("accuracy_health", optional=True): _health,
        }
    ).allow_extra("*")

    def __init__(
        self,
        id=None,
        label=None,
        description=None,
        default_prediction_server=None,
        model=None,
        capabilities=None,
        prediction_usage=None,
        permissions=None,
        service_health=None,
        model_health=None,
        accuracy_health=None,
        importance=None,
    ):
        self.id = id
        self.label = label
        self.description = description
        self.default_prediction_server = default_prediction_server
        self.model = model
        self.capabilities = capabilities
        self.prediction_usage = prediction_usage
        self.permissions = permissions
        self.service_health = service_health
        self.model_health = model_health
        self.accuracy_health = accuracy_health
        self.importance = importance

    def __repr__(self):
        return encode_utf8_if_py2(u"{}({})".format(self.__class__.__name__, self.label or self.id))

    @classmethod
    def create_from_learning_model(
        cls, model_id, label, description=None, default_prediction_server_id=None, importance=None
    ):
        """Create a deployment from a DataRobot model.

        .. versionadded:: v2.17

        Parameters
        ----------
        model_id : str
            id of the DataRobot model to deploy
        label : str
            a human readable label of the deployment
        description : str, optional
            a human readable description of the deployment
        default_prediction_server_id : str, optional
            an identifier of a prediction server to be used as the default prediction server
        importance : str, optional
            deployment importance

        Returns
        -------
        deployment : Deployment
            The created deployment

        Examples
        --------
        .. code-block:: python

            from datarobot import Project, Deployment
            project = Project.get('5506fcd38bd88f5953219da0')
            model = project.get_models()[0]
            deployment = Deployment.create_from_learning_model(model.id, 'New Deployment')
            deployment
            >>> Deployment('New Deployment')
        """

        payload = {"model_id": model_id, "label": label, "description": description}
        if default_prediction_server_id:
            payload["default_prediction_server_id"] = default_prediction_server_id
        if importance:
            payload["importance"] = importance

        url = "{}fromLearningModel/".format(cls._path)
        deployment_id = cls._client.post(url, data=payload).json()["id"]
        return cls.get(deployment_id)

    @classmethod
    def _create_from_custom_model_entity(
        cls,
        custom_model_entity_id,
        label,
        entity_type,
        description=None,
        default_prediction_server_id=None,
        max_wait=DEFAULT_MAX_WAIT,
        importance=None,
    ):
        # check if model package of the custom model image is already created
        existing_model_packages = unpaginate(
            "modelPackages/", {"model_id": custom_model_entity_id}, cls._client
        )

        try:
            model_package_id = next(existing_model_packages)["id"]
        except StopIteration:
            # model package of the custom model entity does not exists,
            # so create one
            if entity_type == CustomModelVersion.__name__:
                field_name = "custom_model_version_id"
                route = "fromCustomModelVersion"
            else:
                field_name = "custom_model_image_id"
                route = "fromCustomModelImage"
            model_package_payload = {field_name: custom_model_entity_id}

            model_package_id = cls._client.post(
                "modelPackages/{}/".format(route), data=model_package_payload
            ).json()["id"]

        # create deployment from the model package
        deployment_payload = {
            "model_package_id": model_package_id,
            "label": label,
            "description": description,
        }
        if default_prediction_server_id:
            deployment_payload["default_prediction_server_id"] = default_prediction_server_id
        if importance:
            deployment_payload["importance"] = importance
        response = cls._client.post(
            "{}fromModelPackage/".format(cls._path), data=deployment_payload
        )

        # wait for LRS job resolution to support making predictions against the deployment
        wait_for_async_resolution(cls._client, response.headers["Location"], max_wait)

        deployment_id = response.json()["id"]
        return cls.get(deployment_id)

    @classmethod
    @deprecated(
        deprecated_since_version="v2.23",
        will_remove_version="v2.24",
        message="The use of CustomModelImages is deprecated. "
        "Use create_from_custom_model_version instead.",
    )
    def create_from_custom_model_image(
        cls,
        custom_model_image_id,
        label,
        description=None,
        default_prediction_server_id=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """Create a deployment from a DataRobot custom model image.

        Parameters
        ----------
        custom_model_image_id : str
            id of the DataRobot custom model image to deploy
        label : str
            a human readable label of the deployment
        description : str, optional
            a human readable description of the deployment
        default_prediction_server_id : str, optional
            an identifier of a prediction server to be used as the default prediction server
        max_wait : int, optional
            seconds to wait for successful resolution of a deployment creation job.
            Deployment supports making predictions only after a deployment creating job
            has successfully finished

        Returns
        -------
        deployment : Deployment
            The created deployment
        """

        return cls._create_from_custom_model_entity(
            custom_model_entity_id=custom_model_image_id,
            label=label,
            entity_type=CustomInferenceImage.__name__,
            description=description,
            default_prediction_server_id=default_prediction_server_id,
            max_wait=max_wait,
        )

    @classmethod
    def create_from_custom_model_version(
        cls,
        custom_model_version_id,
        label,
        description=None,
        default_prediction_server_id=None,
        max_wait=DEFAULT_MAX_WAIT,
        importance=None,
    ):
        """Create a deployment from a DataRobot custom model image.

        Parameters
        ----------
        custom_model_version_id : str
            id of the DataRobot custom model version to deploy
            The version must have a base_environment_id.
        label : str
            a human readable label of the deployment
        description : str, optional
            a human readable description of the deployment
        default_prediction_server_id : str, optional
            an identifier of a prediction server to be used as the default prediction server
        max_wait : int, optional
            seconds to wait for successful resolution of a deployment creation job.
            Deployment supports making predictions only after a deployment creating job
            has successfully finished
        importance : str, optional
            deployment importance

        Returns
        -------
        deployment : Deployment
            The created deployment
        """

        return cls._create_from_custom_model_entity(
            custom_model_entity_id=custom_model_version_id,
            label=label,
            entity_type=CustomModelVersion.__name__,
            description=description,
            default_prediction_server_id=default_prediction_server_id,
            max_wait=max_wait,
            importance=importance,
        )

    @classmethod
    def list(cls, order_by=None, search=None, filters=None):
        """List all deployments a user can view.

        .. versionadded:: v2.17

        Parameters
        ----------
        order_by : str, optional
            (New in version v2.18) the order to sort the deployment list by, defaults to `label`

            Allowed attributes to sort by are:

            * ``label``
            * ``serviceHealth``
            * ``modelHealth``
            * ``accuracyHealth``
            * ``recentPredictions``
            * ``lastPredictionTimestamp``

            If the sort attribute is preceded by a hyphen, deployments will be sorted in descending
            order, otherwise in ascending order.

            For health related sorting, ascending means failing, warning, passing, unknown.
        search : str, optional
            (New in version v2.18) case insensitive search against deployment's
            label and description.
        filters : datarobot.models.deployment.DeploymentListFilters, optional
            (New in version v2.20) an object containing all filters that you'd like to apply to the
            resulting list of deployments. See
            :class:`~datarobot.models.deployment.DeploymentListFilters` for details on usage.

        Returns
        -------
        deployments : list
            a list of deployments the user can view

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployments = Deployment.list()
            deployments
            >>> [Deployment('New Deployment'), Deployment('Previous Deployment')]

        .. code-block:: python

            from datarobot import Deployment
            from datarobot.enums import DEPLOYMENT_SERVICE_HEALTH
            filters = DeploymentListFilters(
                role='OWNER',
                service_health=[DEPLOYMENT_SERVICE_HEALTH.FAILING]
            )
            filtered_deployments = Deployment.list(filters=filters)
            filtered_deployments
            >>> [Deployment('Deployment I Own w/ Failing Service Health')]
        """
        if filters is None:
            filters = DeploymentListFilters()

        param = {}
        if order_by:
            param["order_by"] = order_by
        if search:
            param["search"] = search
        param.update(filters.construct_query_args())
        data = unpaginate(cls._path, param, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, deployment_id):
        """Get information about a deployment.

        .. versionadded:: v2.17

        Parameters
        ----------
        deployment_id : str
            the id of the deployment

        Returns
        -------
        deployment : Deployment
            the queried deployment

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            deployment.id
            >>>'5c939e08962d741e34f609f0'
            deployment.label
            >>>'New Deployment'
        """

        path = "{}{}/".format(cls._path, deployment_id)
        return cls.from_location(path)

    def update(self, label=None, description=None, importance=None):
        """
        Update the label and description of this deployment.

        .. versionadded:: v2.19
        """

        payload = {}
        if label:
            payload["label"] = label
        if description:
            payload["description"] = description
        if importance:
            payload["importance"] = importance
        if not payload:
            raise ValueError("")

        url = "{}{}/".format(self._path, self.id)
        self._client.patch(url, data=payload)

        if label:
            self.label = label
        if description:
            self.description = description

    def delete(self):
        """
        Delete this deployment.

        .. versionadded:: v2.17
        """

        url = "{}{}/".format(self._path, self.id)
        self._client.delete(url)

    def replace_model(self, new_model_id, reason, max_wait=600):
        """Replace the model used in this deployment. To confirm model replacement eligibility, use
         :meth:`~datarobot.Deployment.validate_replacement_model` beforehand.

        .. versionadded:: v2.17

        Model replacement is an asynchronous process, which means some preparatory work may
        be performed after the initial request is completed. This function will not return until all
        preparatory work is fully finished.

        Predictions made against this deployment will start using the new model as soon as the
        initial request is completed. There will be no interruption for predictions throughout
        the process.

        Parameters
        ----------
        new_model_id : str
            The id of the new model to use. If replacing the deployment's model with a
            CustomInferenceModel, a specific CustomModelVersion ID must be used.
        reason : MODEL_REPLACEMENT_REASON
            The reason for the model replacement. Must be one of 'ACCURACY', 'DATA_DRIFT', 'ERRORS',
            'SCHEDULED_REFRESH', 'SCORING_SPEED', or 'OTHER'. This value will be stored in the model
            history to keep track of why a model was replaced
        max_wait : int, optional
            (new in version 2.22) The maximum time to wait for
            model replacement job to complete before erroring

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            deployment.model['id'], deployment.model['type']
            >>>('5c0a979859b00004ba52e431', 'Decision Tree Classifier (Gini)')

            deployment.replace_model('5c0a969859b00004ba52e41b', MODEL_REPLACEMENT_REASON.ACCURACY)
            deployment.model['id'], deployment.model['type']
            >>>('5c0a969859b00004ba52e41b', 'Support Vector Classifier (Linear Kernel)')
        """

        url = "{}{}/model/".format(self._path, self.id)
        payload = {"modelId": new_model_id, "reason": reason}
        response = self._client.patch(url, data=payload)
        deployment_loc = wait_for_async_resolution(
            self._client, response.headers["Location"], max_wait=max_wait
        )
        deployment_id = get_id_from_location(deployment_loc)
        deployment = Deployment.get(deployment_id)
        self.model = deployment.model

        # Update prediction intervals settings and check if the new model can support them
        old_pred_int_settings = self.get_prediction_intervals_settings()
        try:
            if old_pred_int_settings["percentiles"]:
                self.update_prediction_intervals_settings(
                    percentiles=old_pred_int_settings["percentiles"],
                    enabled=old_pred_int_settings["enabled"],
                )
        except Exception:
            # Doing a catch-all here because any errors from prediction intervals should not affect
            # the rest of model replacement. If there are errors, then update deployment to use
            # default prediction intervals settings.
            self.update_prediction_intervals_settings(percentiles=[], enabled=False)

    def validate_replacement_model(self, new_model_id):
        """Validate a model can be used as the replacement model of the deployment.

        .. versionadded:: v2.17

        Parameters
        ----------
        new_model_id : str
            the id of the new model to validate

        Returns
        -------
        status : str
            status of the validation, will be one of 'passing', 'warning' or 'failing'.
            If the status is passing or warning, use :meth:`~datarobot.Deployment.replace_model` to
            perform a model replacement. If the status is failing, refer to ``checks`` for more
            detail on why the new model cannot be used as a replacement.
        message : str
            message for the validation result
        checks : dict
            explain why the new model can or cannot replace the deployment's current model
        """

        url = "{}{}/model/validation/".format(self._path, self.id)
        payload = {"modelId": new_model_id}
        data = from_api(self._client.post(url, data=payload).json())
        return data.get("status"), data.get("message"), data.get("checks")

    def get_features(self):
        """Retrieve the list of features needed to make predictions on this deployment.

        Notes
        -----

        Each `feature` dict contains the following structure:

        - ``name`` : str, feature name
        - ``feature_type`` : str, feature type
        - ``importance`` : float, numeric measure of the relationship strength between
          the feature and target (independent of model or other features)
        - ``date_format`` : str or None, the date format string for how this feature was
          interpreted, null if not a date feature, compatible with
          https://docs.python.org/2/library/time.html#time.strftime.
        - ``known_in_advance`` : bool, whether the feature was selected as known in advance in
          a time series model, false for non-time series models.

        Returns
        -------
        features: list
            a list of `feature` dict

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            features = deployment.get_features()
            features[0]['feature_type']
            >>>'Categorical'
            features[0]['importance']
            >>>0.133
        """
        url = "{}{}/features/".format(self._path, self.id)
        data = unpaginate(url, {}, self._client)
        return from_api([feature for feature in data], keep_null_keys=True)

    def submit_actuals(self, data, batch_size=10000):
        """Submit actuals for processing.
        The actuals submitted will be used to calculate accuracy metrics.

        Parameters
        ----------
        data: list or pandas.DataFrame
        batch_size: the max number of actuals in each request

        If `data` is a list, each item should be a dict-like object with the following keys and
        values; if `data` is a pandas.DataFrame, it should contain the following columns:

        - association_id: str, a unique identifier used with a prediction,
            max length 128 characters
        - actual_value: str or int or float, the actual value of a prediction;
            should be numeric for deployments with regression models or
            string for deployments with classification model
        - was_acted_on: bool, optional, indicates if the prediction was acted on in a way that
            could have affected the actual outcome
        - timestamp: datetime or string in RFC3339 format, optional. If the datetime provided
            does not have a timezone, we assume it is UTC.

        Raises
        ------
        ValueError
            if input data is not a list of dict-like objects or a pandas.DataFrame
            if input data is empty

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment, AccuracyOverTime
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            data = [{
                'association_id': '439917',
                'actual_value': 'True',
                'was_acted_on': True
            }]
            deployment.submit_actuals(data)
        """

        if not isinstance(data, (list, pd.DataFrame)):
            raise ValueError(
                "data should be either a list of dict-like objects or a pandas.DataFrame"
            )

        if not isinstance(batch_size, int) or not batch_size >= 1:
            raise ValueError(
                "batch_size should be an integer and should be greater than or equals to one"
            )

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")

        if not data:
            raise ValueError("data should not be empty")

        url = "{}{}/actuals/fromJSON/".format(self._path, self.id)
        for offset in range(0, len(data), batch_size):
            batch = data[offset : offset + batch_size]
            payload = []
            for item in batch:
                actual = {
                    "associationId": item["association_id"],
                    "actualValue": item["actual_value"],
                }

                # format wasActedOn
                was_acted_on = item.get("was_acted_on")
                if not pd.isna(was_acted_on):
                    actual["wasActedOn"] = item["was_acted_on"]

                # format timestamp
                timestamp = item.get("timestamp")
                if timestamp and not pd.isna(timestamp):
                    timestamp = item["timestamp"]
                    if isinstance(timestamp, datetime):
                        if not timestamp.tzinfo:
                            timestamp = timestamp.replace(tzinfo=pytz.utc)
                        timestamp = timestamp.isoformat()
                    actual["timestamp"] = timestamp

                payload.append(actual)
            response = self._client.post(url, data={"data": payload})
            wait_for_async_resolution(self._client, response.headers["Location"])

    def get_predictions_by_forecast_date_settings(self):
        """Retrieve predictions by forecast date settings of this deployment.

        .. versionadded:: v2.27

        Returns
        -------
        settings : dict
            Predictions by forecast date settings of the deployment is a dict with the following
            format:

            enabled : bool
                Is ''True'' if predictions by forecast date is enabled for this deployment.
                To update this setting, see
                :meth:`~datarobot.Deployment.update_predictions_by_forecast_date_settings`

            column_name : string
                The column name in prediction datasets to be used as forecast date.

            datetime_format : string
                The datetime format of the forecast date column in prediction datasets.
        """

        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json())
        return response_json.get("predictions_by_forecast_date")

    def update_predictions_by_forecast_date_settings(
        self,
        enable_predictions_by_forecast_date,
        forecast_date_column_name=None,
        forecast_date_format=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """Update predictions by forecast date settings of this deployment.

        .. versionadded:: v2.27

        Updating predictions by forecast date setting is an asynchronous process,
        which means some preparatory work may be performed after the initial request is completed.
        This function will not return until all preparatory work is fully finished.

        Example
        -------
        To set predictions by forecast date settings to the same default settings you see when using
        the DataRobot web application, you use your ''Deployment'' object like this:

            >>> deployment.update_predictions_by_forecast_date_settings(
            >>>    enable_predictions_by_forecast_date=True,
            >>>    forecast_date_column_name="date (actual)",
            >>>    forecast_date_format="%Y-%m-%d")

        Parameters
        ----------
        enable_predictions_by_forecast_date : bool
            set to ''True'' if predictions by forecast date is to be turned on or set to ''False''
            if predictions by forecast date is to be turned off.

        forecast_date_column_name: string, optional
            The column name in prediction datasets to be used as forecast date.
            If ''enable_predictions_by_forecast_date'' is set to ''False'',
            then the parameter will be ignored.

        forecast_date_format: string, optional
            The datetime format of the forecast date column in prediction datasets.
            If ''enable_predictions_by_forecast_date'' is set to ''False'',
            then the parameter will be ignored.

        max_wait : int, optional
            seconds to wait for successful
        """

        payload = defaultdict(dict)
        payload["predictions_by_forecast_date"]["enabled"] = enable_predictions_by_forecast_date
        if enable_predictions_by_forecast_date:
            assert forecast_date_column_name, (
                "Please specify 'forecast_date_column_name' or set "
                "'enable_predictions_by_forecast_date' to False"
            )
            assert forecast_date_format, (
                "Please specify 'forecast_date_format' or set "
                "'enable_predictions_by_forecast_date' to False"
            )
            payload["predictions_by_forecast_date"]["column_name"] = forecast_date_column_name
            payload["predictions_by_forecast_date"]["datetime_format"] = forecast_date_format

        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_challenger_models_settings(self):
        """Retrieve challenger models settings of this deployment.

        .. versionadded:: v2.27

        Returns
        -------
        settings : dict
            Challenger models settings of the deployment is a dict with the following format:

            enabled : bool
                Is ''True'' if challenger models is enabled for this deployment. To update
                existing ''challenger_models'' settings, see
                :meth:`~datarobot.Deployment.update_challenger_models_settings`
        """

        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json())
        return response_json.get("challenger_models")

    def update_challenger_models_settings(
        self, challenger_models_enabled, max_wait=DEFAULT_MAX_WAIT
    ):
        """Update challenger models settings of this deployment.

        .. versionadded:: v2.27

        Updating challenger models setting is an asynchronous process, which means some preparatory
        work may be performed after the initial request is completed. This function will not return
        until all preparatory work is fully finished.

        Parameters
        ----------
        challenger_models_enabled : bool
            set to ''True'' if challenger models is to be turned on or set to ''False'' if
            challenger models is to be turned off
        max_wait : int, optional
            seconds to wait for successful resolution
        """

        payload = defaultdict(dict)
        payload["challenger_models"]["enabled"] = challenger_models_enabled
        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_segment_analysis_settings(self):
        """Retrieve segment analysis settings of this deployment.

        .. versionadded:: v2.27

        Returns
        -------
        settings : dict
            Segment analysis settings of the deployment containing two items with keys
            ``enabled`` and ``attributes``, which are further described below.

            enabled : bool
                Set to ''True'' if segment analysis is enabled for this deployment. To update
                existing setting, see
                :meth:`~datarobot.Deployment.update_segment_analysis_settings`

            attributes : list
                To create or update existing segment analysis attributes, see
                :meth:`~datarobot.Deployment.update_segment_analysis_settings`
        """

        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json())
        return response_json.get("segment_analysis")

    def update_segment_analysis_settings(
        self, segment_analysis_enabled, segment_analysis_attributes=None, max_wait=DEFAULT_MAX_WAIT,
    ):
        """Update segment analysis settings of this deployment.

        .. versionadded:: v2.27

        Updating segment analysis setting is an asynchronous process, which means some preparatory
        work may be performed after the initial request is completed. This function will not return
        until all preparatory work is fully finished.

        Parameters
        ----------
        segment_analysis_enabled : bool
            set to ''True'' if segment analysis is to be turned on or set to ''False'' if
            segment analysis is to be turned off

        segment_analysis_attributes: list, optional
            A list of strings that gives the segment attributes selected for tracking.

        max_wait : int, optional
            seconds to wait for successful resolution
        """

        payload = defaultdict(dict)
        payload["segment_analysis"]["enabled"] = segment_analysis_enabled
        if segment_analysis_attributes:
            payload["segment_analysis"]["attributes"] = segment_analysis_attributes
        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_drift_tracking_settings(self):
        """Retrieve drift tracking settings of this deployment.

        .. versionadded:: v2.17

        Returns
        -------
        settings : dict
            Drift tracking settings of the deployment containing two nested dicts with key
            ``target_drift`` and ``feature_drift``, which are further described below.

            ``Target drift`` setting contains:

            enabled : bool
                If target drift tracking is enabled for this deployment. To create or update
                existing ''target_drift'' settings, see
                :meth:`~datarobot.Deployment.update_drift_tracking_settings`

            ``Feature drift`` setting contains:

            enabled : bool
                If feature drift tracking is enabled for this deployment. To create or update
                existing ''feature_drift'' settings, see
                :meth:`~datarobot.Deployment.update_drift_tracking_settings`
        """

        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json())
        return {
            key: value
            for key, value in response_json.items()
            if key in ["target_drift", "feature_drift"]
        }

    def update_drift_tracking_settings(
        self, target_drift_enabled=None, feature_drift_enabled=None, max_wait=DEFAULT_MAX_WAIT
    ):
        """Update drift tracking settings of this deployment.

        .. versionadded:: v2.17

        Updating drift tracking setting is an asynchronous process, which means some preparatory
        work may be performed after the initial request is completed. This function will not return
        until all preparatory work is fully finished.

        Parameters
        ----------
        target_drift_enabled : bool, optional
            if target drift tracking is to be turned on
        feature_drift_enabled : bool, optional
            if feature drift tracking is to be turned on
        max_wait : int, optional
            seconds to wait for successful resolution
        """

        payload = defaultdict(dict)
        if target_drift_enabled is not None:
            payload["targetDrift"]["enabled"] = target_drift_enabled
        if feature_drift_enabled is not None:
            payload["featureDrift"]["enabled"] = feature_drift_enabled
        if not payload:
            raise ValueError()

        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_association_id_settings(self):
        """Retrieve association ID setting for this deployment.

        .. versionadded:: v2.19

        Returns
        -------
        association_id_settings : dict in the following format:
            column_names : list[string], optional
                name of the columns to be used as association ID,
            required_in_prediction_requests : bool, optional
                whether the association ID column is required in prediction requests
        """

        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json(), keep_null_keys=True)
        return response_json.get("association_id")

    def update_association_id_settings(
        self, column_names=None, required_in_prediction_requests=None, max_wait=DEFAULT_MAX_WAIT
    ):
        """Update association ID setting for this deployment.

        .. versionadded:: v2.19

        Parameters
        ----------
        column_names : list[string], optional
            name of the columns to be used as association ID,
            currently only support a list of one string
        required_in_prediction_requests : bool, optional
            whether the association ID column is required in prediction requests
        max_wait : int, optional
            seconds to wait for successful resolution
        """

        payload = defaultdict(dict)

        if column_names:
            payload["associationId"]["columnNames"] = column_names
        if required_in_prediction_requests is not None:
            payload["associationId"][
                "requiredInPredictionRequests"
            ] = required_in_prediction_requests
        if not payload:
            raise ValueError()

        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_predictions_data_collection_settings(self):
        """Retrieve predictions data collection settings of this deployment.

        .. versionadded:: v2.21

        Returns
        -------
        predictions_data_collection_settings : dict in the following format:
            enabled : bool
                If predictions data collection is enabled for this deployment. To update
                existing ''predictions_data_collection'' settings, see
                :meth:`~datarobot.Deployment.update_predictions_data_collection_settings`
        """

        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json(), keep_null_keys=True)
        return response_json.get("predictions_data_collection")

    def update_predictions_data_collection_settings(self, enabled, max_wait=DEFAULT_MAX_WAIT):
        """Update predictions data collection settings of this deployment.

        .. versionadded:: v2.21

        Updating predictions data collection setting is an asynchronous process, which means some
        preparatory work may be performed after the initial request is completed.
        This function will not return until all preparatory work is fully finished.

        Parameters
        ----------
        enabled: bool
            if predictions data collection is to be turned on
        max_wait : int, optional
            seconds to wait for successful resolution
        """
        payload = {"predictionsDataCollection": {"enabled": enabled}}

        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_prediction_warning_settings(self):
        """Retrieve prediction warning settings of this deployment.

        .. versionadded:: v2.19

        Returns
        -------
        settings : dict in the following format:
            enabled : bool
                If target prediction_warning is enabled for this deployment. To create or update
                existing ''prediction_warning'' settings, see
                :meth:`~datarobot.Deployment.update_prediction_warning_settings`

            custom_boundaries : dict or None
                If None default boundaries for a model are used. Otherwise has following keys:
                    upper : float
                        All predictions greater than provided value are considered anomalous
                    lower : float
                        All predictions less than provided value are considered anomalous
        """

        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json())
        return response_json.get("prediction_warning")

    def update_prediction_warning_settings(
        self,
        prediction_warning_enabled,
        use_default_boundaries=None,
        lower_boundary=None,
        upper_boundary=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """Update prediction warning settings of this deployment.

        .. versionadded:: v2.19

        Parameters
        ----------
        prediction_warning_enabled : bool
            If prediction warnings should be turned on.
        use_default_boundaries : bool, optional
            If default boundaries of the model should be used for the deployment.
        upper_boundary : float, optional
            All predictions greater than provided value will be considered anomalous
        lower_boundary : float, optional
            All predictions less than provided value will be considered anomalous
        max_wait : int, optional
            seconds to wait for successful resolution
        """

        payload = defaultdict(dict)
        payload["prediction_warning"]["enabled"] = prediction_warning_enabled
        if use_default_boundaries is True:
            payload["prediction_warning"]["custom_boundaries"] = None
        elif use_default_boundaries is False:
            if upper_boundary is not None and lower_boundary is not None:
                payload["prediction_warning"]["custom_boundaries"] = {
                    "upper": upper_boundary,
                    "lower": lower_boundary,
                }

        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload, keep_attrs={"custom_boundaries"})
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_prediction_intervals_settings(self):
        """ Retrieve prediction intervals settings for this deployment.

        .. versionadded:: v2.19

        Notes
        -----
        Note that prediction intervals are only supported for time series deployments.

        Returns
        -------
        dict in the following format:
            enabled : bool
                Whether prediction intervals are enabled for this deployment
            percentiles : list[int]
                List of enabled prediction intervals sizes for this deployment. Currently we only
                support one percentile at a time.
        """
        url = "{}{}/settings/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json())
        return response_json.get("prediction_intervals")

    def update_prediction_intervals_settings(
        self, percentiles, enabled=True, max_wait=DEFAULT_MAX_WAIT
    ):
        """Update prediction intervals settings for this deployment.

        .. versionadded:: v2.19

        Notes
        -----
        Updating prediction intervals settings is an asynchronous process, which means some
        preparatory work may be performed before the settings request is completed. This function
        will not return until all work is fully finished.

        Note that prediction intervals are only supported for time series deployments.

        Parameters
        ----------
        percentiles : list[int]
            The prediction intervals percentiles to enable for this deployment. Currently we only
            support setting one percentile at a time.
        enabled : bool, optional (defaults to True)
            Whether to enable showing prediction intervals in the results of predictions requested
            using this deployment.
        max_wait : int, optional
            seconds to wait for successful resolution

        Raises
        ------
        AssertionError
            If ``percentiles`` is in an invalid format
        AsyncFailureError
            If any of the responses from the server are unexpected
        AsyncProcessUnsuccessfulError
            If the prediction intervals calculation job has failed or has been cancelled.
        AsyncTimeoutError
            If the prediction intervals calculation job did not resolve in time
        """
        if percentiles:
            # Ensure percentiles is list[int] with length 1
            assert isinstance(percentiles, list) and len(percentiles) == 1

            # Make sure that the requested percentile is calculated
            from .model import DatetimeModel

            model = DatetimeModel(id=self.model["id"], project_id=self.model["project_id"])
            job = model.calculate_prediction_intervals(percentiles[0])
            job.wait_for_completion(max_wait)

        # Now update deployment with new prediction intervals settings
        payload = {"predictionIntervals": {"enabled": enabled, "percentiles": percentiles or []}}
        url = "{}{}/settings/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait)

    def get_service_stats(
        self,
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
            the queried service stats metrics information
        """

        kwargs = {
            "model_id": model_id,
            "start_time": start_time,
            "end_time": end_time,
            "execution_time_quantile": execution_time_quantile,
            "response_time_quantile": response_time_quantile,
            "slow_requests_threshold": slow_requests_threshold,
        }
        return ServiceStats.get(self.id, **kwargs)

    def get_service_stats_over_time(
        self,
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
            the queried service stats metric over time information
        """

        kwargs = {
            "metric": metric,
            "model_id": model_id,
            "start_time": start_time,
            "end_time": end_time,
            "bucket_size": bucket_size,
            "quantile": quantile,
            "threshold": threshold,
        }
        return ServiceStatsOverTime.get(self.id, **kwargs)

    def get_target_drift(self, model_id=None, start_time=None, end_time=None, metric=None):
        """Retrieve target drift information over a certain time period.

        .. versionadded:: v2.21

        Parameters
        ----------
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
        """

        return TargetDrift.get(
            self.id, model_id=model_id, start_time=start_time, end_time=end_time, metric=metric
        )

    def get_feature_drift(self, model_id=None, start_time=None, end_time=None, metric=None):
        """Retrieve drift information for deployment's features over a certain time period.

        .. versionadded:: v2.21

        Parameters
        ----------
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
        """

        return FeatureDrift.list(
            self.id, model_id=model_id, start_time=start_time, end_time=end_time, metric=metric
        )

    def get_accuracy(self, model_id=None, start_time=None, end_time=None, start=None, end=None):
        """Retrieve values of accuracy metrics over a certain time period.

        .. versionadded:: v2.18

        Parameters
        ----------
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
        """
        # For a brief time, we accidentally used the kwargs "start" and "end". We add this logic
        # here to retain backwards compatibility with these legacy kwargs.
        start_time = start_time or start
        end_time = end_time or end

        return Accuracy.get(self.id, model_id=model_id, start_time=start_time, end_time=end_time)

    def get_accuracy_over_time(
        self, metric=None, model_id=None, start_time=None, end_time=None, bucket_size=None
    ):
        """Retrieve information about how an accuracy metric changes over a certain time period.

        .. versionadded:: v2.18

        Parameters
        ----------
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
        """

        return AccuracyOverTime.get(
            self.id,
            metric=metric,
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
            bucket_size=bucket_size,
        )

    def update_secondary_dataset_config(self, secondary_dataset_config_id, credential_ids=None):
        """ Update the secondary dataset config used by Feature discovery model for a
        given deployment.

        .. versionadded:: v2.23

        Parameters
        ----------
        secondary_dataset_config_id: str
            Id of the secondary dataset config
        credential_ids: list or None
            List of DatasetsCredentials used by the secondary datasets

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment(deployment_id='5c939e08962d741e34f609f0')
            config = deployment.update_secondary_dataset_config('5df109112ca582033ff44084')
            config
            >>> '5df109112ca582033ff44084'
        """
        url = "{}{}/model/secondaryDatasetConfiguration/".format(self._path, self.id)
        payload = {"secondaryDatasetConfigId": secondary_dataset_config_id}
        if credential_ids:
            payload["credentialsIds"] = credential_ids
        self._client.patch(url, data=payload)
        return self.get_secondary_dataset_config()

    def get_secondary_dataset_config(self):
        """ Get the secondary dataset config used by Feature discovery model for a
        given deployment.

        .. versionadded:: v2.23

        Returns
        -------
        secondary_dataset_config : SecondaryDatasetConfigurations
            Id of the secondary dataset config

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment(deployment_id='5c939e08962d741e34f609f0')
            deployment.update_secondary_dataset_config('5df109112ca582033ff44084')
            config = deployment.get_secondary_dataset_config()
            config
            >>> '5df109112ca582033ff44084'
        """
        url = "{}{}/model/secondaryDatasetConfiguration/".format(self._path, self.id)
        response_json = from_api(self._client.get(url).json())
        return response_json.get("secondary_dataset_config_id")

    def get_prediction_results(
        self,
        model_id=None,
        start_time=None,
        end_time=None,
        actuals_present=None,
        offset=None,
        limit=None,
    ):
        """Retrieve a list of prediction results of the deployment.

        .. versionadded:: v2.24

        Parameters
        ----------
        model_id : str
            the id of the model
        start_time : datetime
            start of the time period
        end_time : datetime
            end of the time period
        actuals_present : bool
            filters predictions results to only those
            who have actuals present or with missing actuals
        offset : int
            this many results will be skipped
        limit : int
            at most this many results are returned

        Returns
        -------
        prediction_results: list[dict]
            a list of prediction results

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            results = deployment.get_prediction_results()
        """

        url = "{}{}/predictionResults/".format(self._path, self.id)
        params = self._build_query_params(
            start_time,
            end_time,
            model_id=model_id,
            actuals_present=actuals_present,
            offset=offset,
            limit=limit,
        )
        data = self._client.get(url, params=params).json()["data"]
        return from_api([prediction_result for prediction_result in data], keep_null_keys=True)

    def download_prediction_results(
        self,
        filepath,
        model_id=None,
        start_time=None,
        end_time=None,
        actuals_present=None,
        offset=None,
        limit=None,
    ):
        """Download prediction results of the deployment as a CSV file.

        .. versionadded:: v2.24

        Parameters
        ----------
        filepath : str
            path of the csv file
        model_id : str
            the id of the model
        start_time : datetime
            start of the time period
        end_time : datetime
            end of the time period
        actuals_present : bool
            filters predictions results to only those
            who have actuals present or with missing actuals
        offset : int
            this many results will be skipped
        limit : int
            at most this many results are returned

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            results = deployment.download_prediction_results('path_to_prediction_results.csv')
        """

        url = "{}{}/predictionResults/".format(self._path, self.id)
        headers = {"Accept": "text/csv"}
        params = self._build_query_params(
            start_time,
            end_time,
            model_id=model_id,
            actuals_present=actuals_present,
            offset=offset,
            limit=limit,
        )
        response = self._client.get(url, params=params, headers=headers)
        with open(filepath, mode="wb") as file:
            file.write(response.content)

    def download_scoring_code(
        self,
        filepath,
        source_code=False,
        include_agent=False,
        include_prediction_explanations=False,
    ):
        """Retrieve scoring code of the current deployed model.

        .. versionadded:: v2.24

        Notes
        -----
        When setting `include_agent` or `include_predictions_explanations` to `True`,
        it can take a considerably longer time to download the scoring code.

        Parameters
        ----------
        filepath : str
            path of the scoring code file
        source_code : bool
            whether source code or binary of the scoring code will be retrieved
        include_agent : bool
            whether the scoring code retrieved will include tracking agent
        include_prediction_explanations : bool
            whether the scoring code retrieved will include prediction explanations

        Examples
        --------
        .. code-block:: python

            from datarobot import Deployment
            deployment = Deployment.get(deployment_id='5c939e08962d741e34f609f0')
            results = deployment.download_scoring_code('path_to_scoring_code.jar')
        """

        # retrieve the scoring code
        if include_agent or include_prediction_explanations:
            build_url = "{}{}/scoringCodeBuilds/".format(self._path, self.id)
            response = self._client.post(
                build_url,
                data={
                    "includeAgent": include_agent,
                    "includePredictionExplanations": include_prediction_explanations,
                },
            )
            retrieve_url = wait_for_async_resolution(self._client, response.headers["Location"])
            response = self._client.get(retrieve_url)
        else:
            retrieve_url = "{}{}/scoringCode/".format(self._path, self.id)
            params = {
                "sourceCode": source_code,
                "includeAgent": include_agent,
                "includePredictionExplanations": include_prediction_explanations,
            }
            response = self._client.get(retrieve_url, params=params)
        # write to file
        with open(filepath, mode="wb") as file:
            file.write(response.content)


def _check(trafaret, value, default_to_null=True):
    if default_to_null and value is None:
        return None

    # Allow users to pass a single value even if a list of values is expected.
    if isinstance(trafaret, t.List) and not isinstance(value, list):
        value = [value]

    return trafaret.check(value)


class DeploymentListFilters(object):
    def __init__(
        self,
        role=None,
        service_health=None,
        model_health=None,
        accuracy_health=None,
        execution_environment_type=None,
        importance=None,
    ):
        """Construct a set of filters to pass to ``Deployment.list()``

        .. versionadded:: v2.20

        Parameters
        ----------
        role : str
            A user role. If specified, then take those deployments that the user can view, then
            filter them down to those that the user has the specified role for, and return only
            them. Allowed options are ``OWNER`` and ``USER``.
        service_health : list of str
            A list of service health status values. If specified, then only deployments whose
            service health status is one of these will be returned. See
            ``datarobot.enums.DEPLOYMENT_SERVICE_HEALTH_STATUS`` for allowed values.
            Supports comma-separated lists.
        model_health : list of str
            A list of model health status values. If specified, then only deployments whose model
            health status is one of these will be returned. See
            ``datarobot.enums.DEPLOYMENT_MODEL_HEALTH_STATUS`` for allowed values.
            Supports comma-separated lists.
        accuracy_health : list of str
            A list of accuracy health status values. If specified, then only deployments whose
            accuracy health status is one of these will be returned. See
            ``datarobot.enums.DEPLOYMENT_ACCURACY_HEALTH_STATUS`` for allowed values.
            Supports comma-separated lists.
        execution_environment_type : list of str
            A list of strings representing the type of the deployments' execution environment.
            If provided, then only return those deployments whose execution environment type is
            one of those provided. See ``datarobot.enums.DEPLOYMENT_EXECUTION_ENVIRONMENT_TYPE``
            for allowed values. Supports comma-separated lists.
        importance : list of str
            A list of strings representing the deployments' "importance".
            If provided, then only return those deployments whose importance
            is one of those provided. See ``datarobot.enums.DEPLOYMENT_IMPORTANCE``
            for allowed values. Supports comma-separated lists. Note that Approval Workflows must
            be enabled for your account to use this filter, otherwise the API will return a 403.

        Examples
        --------
        Multiple filters can be combined in interesting ways to return very specific subsets of
        deployments.

        *Performing AND logic*

            Providing multiple different parameters will result in AND logic between them.
            For example, the following will return all deployments that I own whose service health
            status is failing.

            .. code-block:: python

                from datarobot import Deployment
                from datarobot.models.deployment import DeploymentListFilters
                from datarobot.enums import DEPLOYMENT_SERVICE_HEALTH
                filters = DeploymentListFilters(
                    role='OWNER',
                    service_health=[DEPLOYMENT_SERVICE_HEALTH.FAILING]
                )
                deployments = Deployment.list(filters=filters)

        **Performing OR logic**

            Some filters support comma-separated lists (and will say so if they do). Providing a
            comma-separated list of values to a single filter performs OR logic between those
            values. For example, the following will return all deployments whose service health
            is either ``warning`` OR ``failing``.

            .. code-block:: python

                from datarobot import Deployment
                from datarobot.models.deployment import DeploymentListFilters
                from datarobot.enums import DEPLOYMENT_SERVICE_HEALTH
                filters = DeploymentListFilters(
                    service_health=[
                        DEPLOYMENT_SERVICE_HEALTH.WARNING,
                        DEPLOYMENT_SERVICE_HEALTH.FAILING,
                    ]
                )
                deployments = Deployment.list(filters=filters)

        Performing OR logic across different filter types is not supported.

        .. note::

            In all cases, you may only retrieve deployments for which you have at least
            the USER role for. Deployments for which you are a CONSUMER of will not be returned,
            regardless of the filters applied.
        """

        self.role = _check(String(), role)
        self.service_health = _check(t.List[String()], service_health)
        self.model_health = _check(t.List[String()], model_health)
        self.accuracy_health = _check(t.List[String()], accuracy_health)
        self.execution_environment_type = _check(t.List[String()], execution_environment_type)
        self.importance = _check(t.List[String()], importance)

    def construct_query_args(self):
        query_args = {}

        if self.role:
            query_args["role"] = self.role
        if self.service_health:
            query_args["serviceHealth"] = self._list_to_comma_separated_string(self.service_health)
        if self.model_health:
            query_args["modelHealth"] = self._list_to_comma_separated_string(self.model_health)
        if self.accuracy_health:
            query_args["accuracyHealth"] = self._list_to_comma_separated_string(
                self.accuracy_health
            )
        if self.execution_environment_type:
            query_args["executionEnvironmentType"] = self._list_to_comma_separated_string(
                self.execution_environment_type
            )
        if self.importance:
            query_args["importance"] = self._list_to_comma_separated_string(self.importance)

        return query_args

    @staticmethod
    def _list_to_comma_separated_string(input_list):
        output_string = ""
        for list_item in input_list:
            output_string += "{},".format(list_item)
        output_string = output_string[:-1]
        return output_string
