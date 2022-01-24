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
import logging

import trafaret as t

from datarobot.client import get_client, staticproperty
from datarobot.models.api_object import APIObject
from datarobot.utils.pagination import unpaginate

logger = logging.getLogger(__package__)


class ModelPackage(APIObject):
    """
    A Model Package.

    Attributes
    ----------
    id : str
        ID of the Model Package
    name : str
        Model Package name
    model_id : str
        ID of the model
    permissions : list(str)
        Permissions the user making the request has for the Model Package.
    model_execution_type
        Type of Model Package. `dedicated` (native DataRobot models) and
        `custom_inference_model` (user added inference models) both execute on DataRobot
        'prediction servers, `external` do not.
    active_deployment_count : int
        Number of deployments currently using this Model Package.
    is_archived : bool
        Whether the Model Package is permanently archived (cannot be used in deployment
        or replacement).
    import_meta : dict
        Information from when this Model Package was first saved.
    source_meta : dict
        Meta information from where this model was generated.
    model_kind : dict
        Model characteristics.
    target : dict
        Information about the target for the Model Package.
    model_description : dict
        Information about the model in the Model Package.
    datasets : dict
        Dataset information for the Model Package.
    timeseries : dict
        Time series information for the Model Package.
    bias_and_fairness : dict
        Bias and fairness settings of the Model Package.
    """

    _client = staticproperty(get_client)
    _base_url = "modelPackages/fromLearningModel/"
    _get_url = "modelPackages/{}/"
    _list_url = "modelPackages/"
    _build_url = "modelPackages/{}/modelPackageFileBuilds/"
    _download_url = "modelPackages/{}/modelPackageFile/"

    _attributes = [
        "id",
        "name",
        "model_id",
        "permissions",
        "model_execution_type",
        "active_deployment_count",
        "is_archived",
        "import_meta",
        "source_meta",
        "model_kind",
        "target",
        "model_description",
        "datasets",
        "timeseries",
        "bias_and_fairness",
    ]

    _import_meta = t.Dict(
        {
            t.Key("creator_id", optional=True): t.String,
            t.Key("creator_username", optional=True): t.String,
            t.Key("date_created", optional=True): t.String,
            t.Key("original_file_name", optional=True): t.String,
        }
    ).ignore_extra("*")

    _scoring_code = t.Dict(
        {
            t.Key("location", optional=True): t.String(allow_blank=True),
            t.Key("data_robot_prediction_version", optional=True): t.String(allow_blank=True),
        }
    ).ignore_extra("*")

    _source_meta = t.Dict(
        {
            t.Key("project_id", optional=True): t.String,
            t.Key("project_name", optional=True): t.String,
            t.Key("environment_url", optional=True): t.String(allow_blank=True),
            t.Key("scoring_code", optional=True): _scoring_code,
        }
    ).ignore_extra("*")

    _model_kind = t.Dict(
        {
            t.Key("is_time_series", optional=True): t.Bool,
            t.Key("is_multiseries", optional=True): t.Bool,
            t.Key("is_unsupervised_learning", optional=True): t.Bool,
            t.Key("is_anomaly_detection_model", optional=True): t.Bool,
            t.Key("is_feature_discovery", optional=True): t.Bool,
        }
    ).ignore_extra("*")

    _target = t.Dict(
        {
            t.Key("name", optional=True): t.String,
            t.Key("type", optional=True): t.String,
            t.Key("class_names", optional=True): t.List(t.String),
            t.Key("class_count", optional=True): t.Int,
            t.Key("prediction_threshold", optional=True): t.Float,
            t.Key("prediction_probabilities_column", optional=True): t.String,
        }
    ).ignore_extra("*")

    _model_description = t.Dict(
        {
            t.Key("description", optional=True): t.String(allow_blank=True),
            t.Key("model_name", optional=True): t.String(allow_blank=True),
            t.Key("location", optional=True): t.String(allow_blank=True),
            t.Key("build_environment_type", optional=True): t.String(allow_blank=True),
        }
    ).ignore_extra("*")

    _datasets = t.Dict(
        {
            t.Key("dataset_name", optional=True): t.String,
            t.Key("training_data_catalog_id", optional=True): t.String,
            t.Key("training_data_size", optional=True): t.Int,
            t.Key("holdout_dataset_name", optional=True): t.String,
            t.Key("holdout_data_catalog_id", optional=True): t.String,
            t.Key("target_histogram_baseline", optional=True): t.String,
            t.Key("baseline_segmented_by", optional=True): t.List(t.String),
        }
    ).ignore_extra("*")

    _timeseries = t.Dict(
        {
            t.Key("datetime_column_name", optional=True): t.String,
            t.Key("forecast_distance_column_name", optional=True): t.String,
            t.Key("forecast_point_column_name", optional=True): t.String,
            t.Key("series_column_name", optional=True): t.String,
            t.Key("datetime_column_format", optional=True): t.String,
            t.Key("forecast_distances", optional=True): t.List(t.Int),
            t.Key("forecast_distances_time_unit", optional=True): t.String,
            t.Key("feature_derivation_window_start", optional=True): t.Int,
            t.Key("feature_derivation_window_end", optional=True): t.Int,
            t.Key("effective_feature_derivation_window_start", optional=True): t.Int,
            t.Key("effective_feature_derivation_window_end", optional=True): t.Int,
            t.Key("is_new_series_support", optional=True): t.Bool,
            t.Key("is_cross_series", optional=True): t.Bool,
            t.Key("is_traditional_time_series", optional=True): t.Bool,
        }
    ).ignore_extra("*")

    _bias_and_fairness = t.Dict(
        {
            t.Key("protected_features", optional=True): t.List(t.String),
            t.Key("preferable_target_value", optional=True): t.Any,
            t.Key("fairness_metrics_set", optional=True): t.String,
            t.Key("fairness_threshold", optional=True): t.Float,
        }
    ).ignore_extra("*")

    _converter = t.Dict(
        {
            t.Key("id"): t.String,
            t.Key("name"): t.String,
            t.Key("model_id"): t.String,
            t.Key("permissions", optional=True): t.List(t.String),
            t.Key("model_execution_type", optional=True): t.String,
            t.Key("active_deployment_count", optional=True): t.Int,
            t.Key("is_archived", optional=True): t.Bool,
            t.Key("import_meta", optional=True): _import_meta,
            t.Key("source_meta", optional=True): _source_meta,
            t.Key("model_kind", optional=True): _model_kind,
            t.Key("target", optional=True): _target,
            t.Key("model_description", optional=True): _model_description,
            t.Key("datasets", optional=True): _datasets,
            t.Key("timeseries", optional=True): _timeseries,
            t.Key("bias_and_fairness", optional=True): _bias_and_fairness,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id=None,
        name=None,
        model_id=None,
        permissions=None,
        model_execution_type=None,
        active_deployment_count=None,
        is_archived=None,
        import_meta=None,
        source_meta=None,
        model_kind=None,
        target=None,
        model_description=None,
        datasets=None,
        timeseries=None,
        bias_and_fairness=None,
    ):
        self.id = id
        self.name = name
        self.model_id = model_id
        self.permissions = permissions
        self.model_execution_type = model_execution_type
        self.active_deployment_count = active_deployment_count
        self.is_archived = is_archived
        self.import_meta = import_meta
        self.source_meta = source_meta
        self.model_kind = model_kind
        self.target = target
        self.model_description = model_description
        self.datasets = datasets
        self.timeseries = timeseries
        self.bias_and_fairness = bias_and_fairness

    @classmethod
    def from_data(cls, data):
        checked = cls._converter.check(data)
        safe_data = cls._filter_data(checked)
        return cls(**safe_data)

    def to_dict(self):
        """ Show Model Package information as a dictionary. """

        out = {attr: getattr(self, attr) for attr in self._attributes}
        return out

    @classmethod
    def create(cls, model_id=None, name=None, prediction_threshold=None):
        """ Create a Model Package.

        Parameters
        ----------
        model_id : str
            The ID of the model to be used in the Model Package.
        name : str
            Optional, the name of the model.
        prediction_threshold : float
            Prediction threshold to use.
        Returns
        -------
        model_package : ModelPackage
            Returns an initialized instance of a ModelPackage.
        """

        payload = {
            "model_id": model_id,
        }
        if name:
            payload["name"] = name
        if prediction_threshold:
            payload["prediction_threshold"] = prediction_threshold

        response = cls._client.post(cls._base_url, data=payload)
        return cls.from_server_data(response.json())

    @classmethod
    def get(cls, model_package_id):
        """ Retrieve information for a single Model Package by id.

        Parameters
        ----------
        model_package_id : basestring
            The id of the Model Package.
        Returns
        -------
        model_package : ModelPackage
            Instance with initialized data.
        """

        return cls.from_location(cls._get_url.format(model_package_id))

    @classmethod
    def list(cls):
        """Retrieve a list of available Model Packages.

        Returns
        -------
        model_package_list : list
            List of Model Packages.
        """

        return [
            cls.from_server_data(x)
            for x in unpaginate(initial_url=cls._list_url, initial_params=None, client=cls._client,)
        ]
