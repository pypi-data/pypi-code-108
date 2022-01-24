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
from datetime import datetime
import warnings
import webbrowser

import pandas as pd
import six
from six.moves.urllib.parse import urljoin
import trafaret as t

from datarobot._compat import Int, String
from datarobot.errors import (
    ClientError,
    JobAlreadyRequested,
    NoRedundancyImpactAvailable,
    ParentModelInsightFallbackWarning,
    ServerError,
)
from datarobot.models.anomaly_assessment import AnomalyAssessmentRecord
from datarobot.models.blueprint import BlueprintTaskDocument, ModelBlueprintChart
from datarobot.models.cluster import Cluster
from datarobot.models.cluster_insight import ClusterInsight
from datarobot.models.confusion_chart import ConfusionChart
from datarobot.models.datetime_trend_plots import (
    AccuracyOverTimePlot,
    AccuracyOverTimePlotPreview,
    AccuracyOverTimePlotsMetadata,
    AnomalyOverTimePlot,
    AnomalyOverTimePlotPreview,
    AnomalyOverTimePlotsMetadata,
    ForecastVsActualPlot,
    ForecastVsActualPlotPreview,
    ForecastVsActualPlotsMetadata,
)
from datarobot.models.external_dataset_scores_insights import ExternalScores
from datarobot.models.feature_effect import (
    FeatureEffectMetadata,
    FeatureEffectMetadataDatetime,
    FeatureEffects,
    FeatureEffectsMulticlass,
)
from datarobot.models.feature_fit import FeatureFit, FeatureFitMetadata, FeatureFitMetadataDatetime
from datarobot.models.lift_chart import LiftChart
from datarobot.models.missing_report import MissingValuesReport
from datarobot.models.pareto_front import ParetoFront
from datarobot.models.residuals import ResidualsChart
from datarobot.models.roc_curve import LabelwiseRocCurve, RocCurve
from datarobot.models.ruleset import Ruleset
from datarobot.models.segmentation import SegmentInfo
from datarobot.models.training_predictions import TrainingPredictions
from datarobot.models.validators import feature_impact_trafaret, multiclass_feature_impact_trafaret
from datarobot.models.word_cloud import WordCloud
from datarobot.utils import datetime_to_string
from datarobot.utils.pagination import unpaginate

from ..enums import (
    CHART_DATA_SOURCE,
    DATETIME_TREND_PLOTS_STATUS,
    DEFAULT_MAX_WAIT,
    MONOTONICITY_FEATURELIST_DEFAULT,
    SOURCE_TYPE,
)
from ..utils import encode_utf8_if_py2, from_api, get_id_from_response, parse_time
from ..utils.deprecation import deprecated, deprecation_warning
from .advanced_tuning import AdvancedTuningSession
from .api_object import APIObject


class Model(APIObject):
    """A model trained on a project's dataset capable of making predictions

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float or None
        the percentage of the project dataset used in training the model.  If the project uses
        datetime partitioning, the sample_pct will be None.  See `training_row_count`,
        `training_duration`, and `training_start_date` and `training_end_date` instead.
    training_row_count : int or None
        the number of rows of the project dataset used in training the model.  In a datetime
        partitioned project, if specified, defines the number of rows used to train the model and
        evaluate backtest scores; if unspecified, either `training_duration` or
        `training_start_date` and `training_end_date` was used to determine that instead.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    is_n_clusters_dynamically_determined : bool
        (New in version v2.27) optional, if this model determines number of clusters dynamically
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    monotonic_increasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically increasing relationship to the target.
        If None, no such constraints are enforced.
    monotonic_decreasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically decreasing relationship to the target.
        If None, no such constraints are enforced.
    n_clusters : int
        (New in version v2.27) optional, number of data clusters discovered by model
    has_empty_clusters: bool
        (New in version v2.27) optional, whether clustering models produces empty clusters.
    supports_monotonic_constraints : bool
        optinonal, whether this model supports enforcing monotonic constraints
    is_starred : bool
        whether this model marked as starred
    prediction_threshold : float
        for binary classification projects, the threshold used for predictions
    prediction_threshold_read_only : bool
        indicated whether modification of the prediction threshold is forbidden. Threshold
        modification is forbidden once a model has had a deployment created or predictions made via
        the dedicated prediction API.
    model_number : integer
        model number assigned to a model
    parent_model_id : str or None
        (New in version v2.20) the id of the model that tuning parameters are derived from
    use_project_settings : bool or None
        (New in version v2.20) Only present for models in datetime-partitioned projects. If
        ``True``, indicates that the custom backtest partitioning settings specified by the user
        were used to train the model and evaluate backtest scores.
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this model is supported in the Composable ML.
    """

    _base_model_path_template = "projects/{}/models/"
    _converter = t.Dict(
        {
            t.Key("id", optional=True): String,
            t.Key("processes", optional=True): t.List(String),
            t.Key("featurelist_name", optional=True): String,
            t.Key("featurelist_id", optional=True): String,
            t.Key("project_id", optional=True): String,
            t.Key("sample_pct", optional=True): t.Float,
            t.Key("training_row_count", optional=True): Int,
            t.Key("training_duration", optional=True): String,
            t.Key("training_start_date", optional=True): parse_time,
            t.Key("training_end_date", optional=True): parse_time,
            t.Key("model_type", optional=True): String,
            t.Key("model_category", optional=True): String,
            t.Key("is_frozen", optional=True): t.Bool,
            t.Key("is_n_clusters_dynamically_determined", optional=True): t.Bool,
            t.Key("blueprint_id", optional=True): String,
            t.Key("metrics", optional=True): t.Dict().allow_extra("*"),
            t.Key("monotonic_increasing_featurelist_id", optional=True): String() | t.Null(),
            t.Key("monotonic_decreasing_featurelist_id", optional=True): String() | t.Null(),
            t.Key("n_clusters", optional=True): Int,
            t.Key("has_empty_clusters", optional=True): t.Bool(),
            t.Key("supports_monotonic_constraints", optional=True): t.Bool(),
            t.Key("is_starred", optional=True): t.Bool(),
            t.Key("prediction_threshold", optional=True): t.Float,
            t.Key("prediction_threshold_read_only", optional=True): t.Bool,
            t.Key("model_number", optional=True): Int,
            t.Key("parent_model_id", optional=True): String() | t.Null,
            t.Key("useProjectSettings", optional=True): t.Bool,
            t.Key("supports_composable_ml", optional=True): t.Bool,
        }
    ).allow_extra("*")

    def __init__(
        self,
        id=None,
        processes=None,
        featurelist_name=None,
        featurelist_id=None,
        project_id=None,
        sample_pct=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        model_type=None,
        model_category=None,
        is_frozen=None,
        is_n_clusters_dynamically_determined=None,
        blueprint_id=None,
        metrics=None,
        project=None,
        data=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        n_clusters=None,
        has_empty_clusters=None,
        supports_monotonic_constraints=None,
        is_starred=None,
        prediction_threshold=None,
        prediction_threshold_read_only=None,
        model_number=None,
        parent_model_id=None,
        use_project_settings=None,
        supports_composable_ml=None,
    ):
        if isinstance(id, dict):
            deprecation_warning(
                "Instantiating Model with a dict",
                deprecated_since_version="v2.3",
                will_remove_version="v3.0",
                message="Use Model.from_data instead",
            )
            self.__init__(**id)
        elif data:
            deprecation_warning(
                "Use of the data keyword argument to Model",
                deprecated_since_version="v2.3",
                will_remove_version="v3.0",
                message="Use Model.from_data instead",
            )
            self.__init__(**data)
        elif isinstance(id, tuple):
            deprecation_warning(
                "Instantiating Model with a tuple",
                deprecated_since_version="v2.3",
                will_remove_version="v3.0",
                message="Use Model.get instead",
            )
            from . import Project

            model_id = id[1]
            project_instance = Project(id[0])
            self.__init__(id=model_id, project=project_instance, project_id=id[0])
        else:
            # Public attributes
            self.id = id
            self.processes = processes
            self.featurelist_name = featurelist_name
            self.featurelist_id = featurelist_id
            self.project_id = project_id
            self.sample_pct = sample_pct
            self.training_row_count = training_row_count
            self.training_duration = training_duration
            self.training_start_date = training_start_date
            self.training_end_date = training_end_date
            self.model_type = model_type
            self.model_category = model_category
            self.is_frozen = is_frozen
            self.is_n_clusters_dynamically_determined = is_n_clusters_dynamically_determined
            self.blueprint_id = blueprint_id
            self.metrics = metrics
            self.monotonic_increasing_featurelist_id = monotonic_increasing_featurelist_id
            self.monotonic_decreasing_featurelist_id = monotonic_decreasing_featurelist_id
            self.n_clusters = n_clusters
            self.has_empty_clusters = has_empty_clusters
            self.supports_monotonic_constraints = supports_monotonic_constraints
            self.is_starred = is_starred
            self.prediction_threshold = prediction_threshold
            self.prediction_threshold_read_only = prediction_threshold_read_only
            self.model_number = model_number
            self.parent_model_id = parent_model_id
            self.use_project_settings = use_project_settings
            self.supports_composable_ml = supports_composable_ml

            # Private attributes
            self._base_model_path = self._base_model_path_template.format(self.project_id)

            # Deprecated attributes
            self._project = project
            self._featurelist = None
            self._blueprint = None

            self._make_objects()

    def __repr__(self):
        return "Model({!r})".format(self.model_type or self.id)

    @property
    @deprecated(
        deprecated_since_version="v2.3",
        will_remove_version="v3.0",
        message="Use Model.project_id instead",
    )
    def project(self):
        return self._project

    @property
    @deprecated(
        deprecated_since_version="v2.3",
        will_remove_version="v3.0",
        message="Use Model.blueprint_id instead",
    )
    def blueprint(self):
        return self._blueprint

    @property
    @deprecated(
        deprecated_since_version="v2.3",
        will_remove_version="v3.0",
        message="Use Model.featurelist_id instead",
    )
    def featurelist(self):
        return self._featurelist

    def _make_objects(self):
        """These objects are deprecated, but that doesn't mean people haven't already begun
        to rely on them"""
        from . import Blueprint, Featurelist, Project

        def _nonefree(d):
            return {k: v for k, v in d.items() if v is not None}

        # Construction Project
        if not self._project:
            self._project = Project(id=self.project_id)

        # Construction Blueprint
        bp_data = {
            "id": self.blueprint_id,
            "processes": self.processes,
            "model_type": self.model_type,
            "project_id": self.project_id,
            "supports_composable_ml": self.supports_composable_ml,
        }
        self._blueprint = Blueprint.from_data(_nonefree(bp_data))

        # Construction FeatureList
        ft_list_data = {
            "id": self.featurelist_id,
            "project_id": self.project_id,
            "name": self.featurelist_name,
        }
        self._featurelist = Featurelist.from_data(_nonefree(ft_list_data))

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        """
        Overrides the inherited method since the model must _not_ recursively change casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        keep_attrs : list
            List of attribute namespaces like: `['top.middle.bottom']`, that should be kept
            even if their values are `None`
        """
        case_converted = from_api(data, do_recursive=False, keep_attrs=keep_attrs)
        return cls.from_data(case_converted)

    @classmethod
    def get(cls, project, model_id):
        """
        Retrieve a specific model.

        Parameters
        ----------
        project : str
            The project's id.
        model_id : str
            The ``model_id`` of the leaderboard item to retrieve.

        Returns
        -------
        model : Model
            The queried instance.

        Raises
        ------
        ValueError
            passed ``project`` parameter value is of not supported type
        """
        from . import Project

        if isinstance(project, Project):
            deprecation_warning(
                "Using a project instance in model.get",
                deprecated_since_version="v2.3",
                will_remove_version="v3.0",
                message="Please use a project ID instead",
            )
            project_id = project.id
            project_instance = project
        elif isinstance(project, six.string_types):
            project_id = project
            project_instance = Project.get(project_id)
        else:
            raise ValueError("Project arg can be Project instance or str")

        if project_instance.is_datetime_partitioned:
            return DatetimeModel.get(project=project_id, model_id=model_id)
        else:
            url = cls._base_model_path_template.format(project_id) + model_id + "/"
            resp_data = cls._server_data(url)
            safe_data = cls._safe_data(resp_data)
            return cls(**dict(safe_data, project=project_instance))

    @classmethod
    @deprecated(deprecated_since_version="v2.3", will_remove_version="v3.0")
    def fetch_resource_data(cls, url, join_endpoint=True):
        """
        (Deprecated.) Used to acquire model data directly from its url.

        Consider using `get` instead, as this is a convenience function
        used for development of datarobot

        Parameters
        ----------
        url : str
            The resource we are acquiring
        join_endpoint : boolean, optional
            Whether the client's endpoint should be joined to the URL before
            sending the request. Location headers are returned as absolute
            locations, so will _not_ need the endpoint

        Returns
        -------
        model_data : dict
            The queried model's data
        """
        return cls._server_data(url)

    def get_features_used(self):
        """Query the server to determine which features were used.

        Note that the data returned by this method is possibly different
        than the names of the features in the featurelist used by this model.
        This method will return the raw features that must be supplied in order
        for predictions to be generated on a new set of data. The featurelist,
        in contrast, would also include the names of derived features.

        Returns
        -------
        features : list of str
            The names of the features used in the model.
        """
        url = "{}{}/features/".format(self._base_model_path, self.id)
        resp_data = self._client.get(url).json()
        return resp_data["featureNames"]

    def get_supported_capabilities(self):
        """Retrieves a summary of the capabilities supported by a model.

        .. versionadded:: v2.14

        Returns
        -------
        supportsBlending: bool
            whether the model supports blending
        supportsMonotonicConstraints: bool
            whether the model supports monotonic constraints
        hasWordCloud: bool
            whether the model has word cloud data available
        eligibleForPrime: bool
            whether the model is eligible for Prime
        hasParameters: bool
            whether the model has parameters that can be retrieved
        supportsCodeGeneration: bool
            (New in version v2.18) whether the model supports code generation
        supportsShap: bool
            (New in version v2.18) True if the model supports Shapley package. i.e. Shapley based
             feature Importance
        supportsEarlyStopping: bool
            (New in version v2.22) `True` if this is an early stopping
            tree-based model and number of trained iterations can be retrieved.
        """

        url = "projects/{}/models/{}/supportedCapabilities/".format(self.project_id, self.id)
        response = self._client.get(url)
        return response.json()

    def get_num_iterations_trained(self):
        """Retrieves the number of estimators trained by early-stopping tree-based models.

        -- versionadded:: v2.22


        Returns
        -------
        projectId: str
            id of project containing the model
        modelId: str
            id of the model
        data: array
            list of `numEstimatorsItem` objects, one for each modeling stage.

        `numEstimatorsItem` will be of the form:

        stage: str
            indicates the modeling stage (for multi-stage models); None of single-stage models
        numIterations: int
         the number of estimators or iterations trained by the model
        """
        url = "projects/{}/models/{}/numIterationsTrained/".format(self.project_id, self.id)
        response = self._client.get(url)
        return response.json()

    def delete(self):
        """
        Delete a model from the project's leaderboard.
        """
        self._client.delete(self._get_model_url())

    def get_leaderboard_ui_permalink(self):
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to this model at leaderboard.
        """
        return "{}/{}{}".format(self._client.domain, self._base_model_path, self.id)

    def open_model_browser(self):
        """
        Opens model at project leaderboard in web browser.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.
        """

        url = self.get_leaderboard_ui_permalink()
        return webbrowser.open(url)

    def train(
        self,
        sample_pct=None,
        featurelist_id=None,
        scoring_type=None,
        training_row_count=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
    ):
        """
        Train the blueprint used in model on a particular featurelist or amount of data.

        This method creates a new training job for worker and appends it to
        the end of the queue for this project.
        After the job has finished you can get the newly trained model by retrieving
        it from the project leaderboard, or by retrieving the result of the job.

        Either `sample_pct` or `training_row_count` can be used to specify the amount of data to
        use, but not both.  If neither are specified, a default of the maximum amount of data that
        can safely be used to train any blueprint without going into the validation data will be
        selected.

        In smart-sampled projects, `sample_pct` and `training_row_count` are assumed to be in terms
        of rows of the minority class.

        .. note:: For datetime partitioned projects, see :meth:`train_datetime
            <datarobot.models.DatetimeModel.train_datetime>` instead.

        Parameters
        ----------
        sample_pct : float, optional
            The amount of data to use for training, as a percentage of the project dataset from
            0 to 100.
        featurelist_id : str, optional
            The identifier of the featurelist to use. If not defined, the
            featurelist of this model is used.
        scoring_type : str, optional
            Either ``SCORING_TYPE.validation`` or
            ``SCORING_TYPE.cross_validation``. ``SCORING_TYPE.validation``
            is available for every partitioning type, and indicates that
            the default model validation should be used for the project.
            If the project uses a form of cross-validation partitioning,
            ``SCORING_TYPE.cross_validation`` can also be used to indicate
            that all of the available training/validation combinations
            should be used to evaluate the model.
        training_row_count : int, optional
            The number of rows to use to train the requested model.
        monotonic_increasing_featurelist_id : str
            (new in version 2.11) optional, the id of the featurelist that defines
            the set of features with a monotonically increasing relationship to the target.
            Passing ``None`` disables increasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.
        monotonic_decreasing_featurelist_id : str
            (new in version 2.11) optional, the id of the featurelist that defines
            the set of features with a monotonically decreasing relationship to the target.
            Passing ``None`` disables decreasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.

        Returns
        -------
        model_job_id : str
            id of created job, can be used as parameter to ``ModelJob.get``
            method or ``wait_for_async_model_creation`` function

        Examples
        --------
        .. code-block:: python

            project = Project.get('project-id')
            model = Model.get('project-id', 'model-id')
            model_job_id = model.train(training_row_count=project.max_train_rows)
        """
        url = self._base_model_path
        if sample_pct is not None and training_row_count is not None:
            raise ValueError("sample_pct and training_row_count cannot both be specified")
        # None values get stripped out in self._client's post method
        payload = {
            "blueprint_id": self.blueprint_id,
            "samplePct": sample_pct,
            "training_row_count": training_row_count,
            "scoring_type": scoring_type,
            "featurelist_id": featurelist_id if featurelist_id is not None else self.featurelist_id,
        }

        if monotonic_increasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_increasing_featurelist_id"] = monotonic_increasing_featurelist_id
        if monotonic_decreasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_decreasing_featurelist_id"] = monotonic_decreasing_featurelist_id
        response = self._client.post(
            url,
            data=payload,
            keep_attrs=[
                "monotonic_increasing_featurelist_id",
                "monotonic_decreasing_featurelist_id",
            ],
        )

        return get_id_from_response(response)

    def train_datetime(
        self,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        time_window_sample_pct=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        use_project_settings=False,
        sampling_method=None,
    ):
        """Trains this model on a different featurelist or sample size.

        Requires that this model is part of a datetime partitioned project; otherwise, an error will
        occur.

        All durations should be specified with a duration string such as those returned
        by the :meth:`partitioning_methods.construct_duration_string
        <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
        Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
        for more information on duration strings.

        Parameters
        ----------
        featurelist_id : str, optional
            the featurelist to use to train the model.  If not specified, the featurelist of this
            model is used.
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            neither ``training_duration`` nor ``use_project_settings`` may be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, neither ``training_row_count`` nor ``use_project_settings`` may be
            specified.
        use_project_settings : bool, optional
            (New in version v2.20) defaults to ``False``. If ``True``, indicates that the custom
            backtest partitioning settings specified by the user will be used to train the model and
            evaluate backtest scores. If specified, neither ``training_row_count`` nor
            ``training_duration`` may be specified.
        time_window_sample_pct : int, optional
            may only be specified when the requested model is a time window (e.g. duration or start
            and end dates). An integer between 1 and 99 indicating the percentage to sample by
            within the window. The points kept are determined by a random uniform sample.
            If specified, training_duration must be specified otherwise, the number of rows used
            to train the model and evaluate backtest scores and an error will occur.
        sampling_method : str, optional
            (New in version v2.23) defines the way training data is selected. Can be either
            ``random`` or ``latest``.  In combination with ``training_row_count`` defines how rows
            are selected from backtest (``latest`` by default).  When training data is defined using
            time range (``training_duration`` or ``use_project_settings``) this setting changes the
            way ``time_window_sample_pct`` is applied (``random`` by default).  Applicable to OTV
            projects only.
        monotonic_increasing_featurelist_id : str, optional
            (New in version v2.18) optional, the id of the featurelist that defines
            the set of features with a monotonically increasing relationship to the target.
            Passing ``None`` disables increasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.
        monotonic_decreasing_featurelist_id : str, optional
            (New in version v2.18) optional, the id of the featurelist that defines
            the set of features with a monotonically decreasing relationship to the target.
            Passing ``None`` disables decreasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.

        Returns
        -------
        job : ModelJob
            the created job to build the model
        """
        from .modeljob import ModelJob

        url = "projects/{}/datetimeModels/".format(self.project_id)
        flist_id = featurelist_id or self.featurelist_id
        payload = {"blueprint_id": self.blueprint_id, "featurelist_id": flist_id}
        if training_row_count:
            payload["training_row_count"] = training_row_count
        if training_duration:
            payload["training_duration"] = training_duration
        if time_window_sample_pct:
            payload["time_window_sample_pct"] = time_window_sample_pct
        if sampling_method:
            payload["sampling_method"] = sampling_method
        if monotonic_increasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_increasing_featurelist_id"] = monotonic_increasing_featurelist_id
        if monotonic_decreasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_decreasing_featurelist_id"] = monotonic_decreasing_featurelist_id
        if use_project_settings:
            payload["use_project_settings"] = use_project_settings
        response = self._client.post(
            url,
            data=payload,
            keep_attrs=[
                "monotonic_increasing_featurelist_id",
                "monotonic_decreasing_featurelist_id",
            ],
        )
        return ModelJob.from_id(self.project_id, get_id_from_response(response))

    def retrain(
        self, sample_pct=None, featurelist_id=None, training_row_count=None, n_clusters=None
    ):
        """Submit a job to the queue to train a blender model.

        Parameters
        ----------
        sample_pct: str, optional
            The sample size in percents (1 to 100) to use in training. If this parameter is used
            then training_row_count should not be given.
        featurelist_id : str, optional
            The featurelist id
        training_row_count : str, optional
            The number of rows used to train the model. If this parameter is used, then sample_pct
            should not be given.
        n_clusters: int, optional
            (new in version 2.27) number of clusters to use in an unsupervised clustering model.
            This parameter is used only for unsupervised clustering models that do not determine
            the number of clusters automatically.

        Returns
        -------
        job : ModelJob
            The created job that is retraining the model
        """
        from .modeljob import ModelJob

        url = "projects/{}/models/fromModel/".format(self.project_id)
        payload = {
            "modelId": self.id,
            "featurelistId": featurelist_id,
            "samplePct": sample_pct,
            "trainingRowCount": training_row_count,
        }
        if n_clusters:
            payload["nClusters"] = n_clusters
        response = self._client.post(url, data=payload)
        return ModelJob.from_id(self.project_id, get_id_from_response(response))

    def _get_model_url(self):
        if self.id is None:
            # This check is why this is a method instead of an attribute. Once we stop creating
            # models without model id's in the tests, we can make this an attribute we set in the
            # constructor.
            raise ValueError("Sorry, id attribute is None so I can't make the url to this model.")
        return "{}{}/".format(self._base_model_path, self.id)

    def request_predictions(
        self,
        dataset_id,
        include_prediction_intervals=None,
        prediction_intervals_size=None,
        forecast_point=None,
        predictions_start_date=None,
        predictions_end_date=None,
        actual_value_column=None,
        explanation_algorithm=None,
        max_explanations=None,
    ):
        """Requests predictions against a previously uploaded dataset.

        Parameters
        ----------
        dataset_id : string
            The dataset to make predictions against (as uploaded from Project.upload_dataset)
        include_prediction_intervals : bool, optional
            (New in v2.16) For :ref:`time series <time_series>` projects only.
            Specifies whether prediction intervals should be calculated for this request. Defaults
            to True if `prediction_intervals_size` is specified, otherwise defaults to False.
        prediction_intervals_size : int, optional
            (New in v2.16) For :ref:`time series <time_series>` projects only.
            Represents the percentile to use for the size of the prediction intervals. Defaults to
            80 if `include_prediction_intervals` is True. Prediction intervals size must be
            between 1 and 100 (inclusive).
        forecast_point : datetime.datetime or None, optional
            (New in version v2.20) For time series projects only. This is the default point relative
            to which predictions will be generated, based on the forecast window of the project. See
            the time series :ref:`prediction documentation <time_series_predict>` for more
            information.
        predictions_start_date : datetime.datetime or None, optional
            (New in version v2.20) For time series projects only. The start date for bulk
            predictions. Note that this parameter is for generating historical predictions using the
            training data. This parameter should be provided in conjunction with
            ``predictions_end_date``. Can't be provided with the ``forecast_point`` parameter.
        predictions_end_date : datetime.datetime or None, optional
            (New in version v2.20) For time series projects only. The end date for bulk
            predictions, exclusive. Note that this parameter is for generating historical
            predictions using the training data. This parameter should be provided in conjunction
            with ``predictions_start_date``. Can't be provided with the
            ``forecast_point`` parameter.
        actual_value_column : string, optional
            (New in version v2.21) For time series unsupervised projects only.
            Actual value column can be used to calculate the classification metrics and
            insights on the prediction dataset. Can't be provided with the ``forecast_point``
            parameter.
        explanation_algorithm: (New in version v2.21) optional; If set to 'shap', the
            response will include prediction explanations based on the SHAP explainer (SHapley
            Additive exPlanations). Defaults to null (no prediction explanations).
        max_explanations: (New in version v2.21) optional; specifies the maximum number of
            explanation values that should be returned for each row, ordered by absolute value,
            greatest to least. If null, no limit. In the case of 'shap': if the number of features
            is greater than the limit, the sum of remaining values will also be returned as
            `shapRemainingTotal`. Defaults to null. Cannot be set if `explanation_algorithm` is
            omitted.

        Returns
        -------
        job : PredictJob
            The job computing the predictions
        """
        # Cannot specify a prediction_intervals_size if include_prediction_intervals=False
        if (
            include_prediction_intervals is not None
            and not include_prediction_intervals
            and prediction_intervals_size is not None
        ):
            raise ValueError(
                "Prediction intervals size cannot be specified if "
                "include_prediction_intervals = False"
            )

        # validate interval size if provided
        if prediction_intervals_size is not None:
            if prediction_intervals_size < 1 or prediction_intervals_size > 100:
                raise ValueError("Prediction intervals size must be between 1 and 100 (inclusive).")

        data = {
            "model_id": self.id,
            "dataset_id": dataset_id,
            "include_prediction_intervals": include_prediction_intervals,
            "prediction_intervals_size": prediction_intervals_size,
        }

        if forecast_point:
            if not isinstance(forecast_point, datetime):
                raise ValueError("forecast_point must be an instance of datetime.datetime")
            data["forecast_point"] = datetime_to_string(forecast_point)
        if predictions_start_date:
            if not isinstance(predictions_start_date, datetime):
                raise ValueError("predictions_start_date must be an instance of datetime.datetime")
            data["predictions_start_date"] = datetime_to_string(predictions_start_date)
        if predictions_end_date:
            if not isinstance(predictions_end_date, datetime):
                raise ValueError("predictions_end_date must be an instance of datetime.datetime")
            data["predictions_end_date"] = datetime_to_string(predictions_end_date)
        data["actual_value_column"] = actual_value_column
        if explanation_algorithm:
            data["explanation_algorithm"] = explanation_algorithm
            if max_explanations:
                data["max_explanations"] = max_explanations

        from .predict_job import PredictJob

        url = "projects/{}/predictions/".format(self.project_id)
        response = self._client.post(url, data=data)
        job_id = get_id_from_response(response)
        return PredictJob.from_id(self.project_id, job_id)

    def _get_feature_impact_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_model_url() + "featureImpact/"

    def get_feature_impact(self, with_metadata=False):
        """
        Retrieve the computed Feature Impact results, a measure of the relevance of each
        feature in the model.

        Feature Impact is computed for each column by creating new data with that column randomly
        permuted (but the others left unchanged), and seeing how the error metric score for the
        predictions is affected. The 'impactUnnormalized' is how much worse the error metric score
        is when making predictions on this modified data. The 'impactNormalized' is normalized so
        that the largest value is 1. In both cases, larger values indicate more important features.

        If a feature is a redundant feature, i.e. once other features are considered it doesn't
        contribute much in addition, the 'redundantWith' value is the name of feature that has the
        highest correlation with this feature. Note that redundancy detection is only available for
        jobs run after the addition of this feature. When retrieving data that predates this
        functionality, a NoRedundancyImpactAvailable warning will be used.

        Elsewhere this technique is sometimes called 'Permutation Importance'.

        Requires that Feature Impact has already been computed with
        :meth:`request_feature_impact <datarobot.models.Model.request_feature_impact>`.

        Parameters
        ----------
        with_metadata : bool
            The flag indicating if the result should include the metadata as well.

        Returns
        -------
        list or dict
            The feature impact data response depends on the with_metadata parameter. The response is
            either a dict with metadata and a list with actual data or just a list with that data.

            Each List item is a dict with the keys ``featureName``, ``impactNormalized``, and
            ``impactUnnormalized``, ``redundantWith`` and ``count``.

            For dict response available keys are:

              - ``featureImpacts`` - Feature Impact data as a dictionary. Each item is a dict with
                    keys: ``featureName``, ``impactNormalized``, and ``impactUnnormalized``, and
                    ``redundantWith``.
              - ``shapBased`` - A boolean that indicates whether Feature Impact was calculated using
                    Shapley values.
              - ``ranRedundancyDetection`` - A boolean that indicates whether redundant feature
                    identification was run while calculating this Feature Impact.
              - ``rowCount`` - An integer or None that indicates the number of rows that was used to
                    calculate Feature Impact. For the Feature Impact calculated with the default
                    logic, without specifying the rowCount, we return None here.
              - ``count`` - An integer with the number of features under the ``featureImpacts``.

        Raises
        ------
        ClientError (404)
            If the feature impacts have not been computed.
        """
        data = self._client.get(self._get_feature_impact_url()).json()
        valid_vata = feature_impact_trafaret.check(data)
        if not valid_vata["ranRedundancyDetection"]:
            warnings.warn(
                "Redundancy detection is not available for this model",
                NoRedundancyImpactAvailable,
                stacklevel=2,
            )
        from .job import filter_feature_impact_result

        return filter_feature_impact_result(valid_vata, with_metadata=with_metadata)

    def get_multiclass_feature_impact(self):
        """
        For multiclass it's possible to calculate feature impact separately for each target class.
        The method for calculation is exactly the same, calculated in one-vs-all style for each
        target class.

        Requires that Feature Impact has already been computed with
        :meth:`request_feature_impact <datarobot.models.Model.request_feature_impact>`.

        Returns
        -------
        feature_impacts : list of dict
           The feature impact data. Each item is a dict with the keys 'featureImpacts' (list),
           'class' (str). Each item in 'featureImpacts' is a dict with the keys 'featureName',
           'impactNormalized', and 'impactUnnormalized', and 'redundantWith'.

        Raises
        ------
        ClientError (404)
            If the multiclass feature impacts have not been computed.
        """
        url = self._get_model_url() + "multiclassFeatureImpact/"
        data = self._client.get(url).json()
        data = multiclass_feature_impact_trafaret.check(data)
        return data["classFeatureImpacts"]

    def request_feature_impact(self, row_count=None, with_metadata=False):
        """
        Request feature impacts to be computed for the model.

        See :meth:`get_feature_impact <datarobot.models.Model.get_feature_impact>` for more
        information on the result of the job.

        Parameters
        ----------
        row_count : int
            The sample size (specified in rows) to use for Feature Impact computation. This is not
            supported for unsupervised, multi-class (that has a separate method) and time series
            projects.

        Returns
        -------
         job : Job
            A Job representing the feature impact computation. To get the completed feature impact
            data, use `job.get_result` or `job.get_result_when_complete`.

        Raises
        ------
        JobAlreadyRequested (422)
            If the feature impacts have already been requested.
        """
        from .job import FeatureImpactJob

        route = self._get_feature_impact_url()
        payload = {"row_count": row_count} if row_count is not None else {}
        response = self._client.post(route, data=payload)
        job_id = get_id_from_response(response)
        return FeatureImpactJob.get(self.project_id, job_id, with_metadata=with_metadata)

    def request_external_test(self, dataset_id, actual_value_column=None):
        """
        Request external test to compute scores and insights on an external test dataset

        Parameters
        ----------
        dataset_id : string
            The dataset to make predictions against (as uploaded from Project.upload_dataset)
        actual_value_column : string, optional
            (New in version v2.21) For time series unsupervised projects only.
            Actual value column can be used to calculate the classification metrics and
            insights on the prediction dataset. Can't be provided with the ``forecast_point``
            parameter.
        Returns
        -------
        job : Job
            a Job representing external dataset insights computation

        """
        return ExternalScores.create(self.project_id, self.id, dataset_id, actual_value_column)

    def get_or_request_feature_impact(self, max_wait=DEFAULT_MAX_WAIT, **kwargs):
        """
        Retrieve feature impact for the model, requesting a job if it hasn't been run previously

        Parameters
        ----------
        max_wait : int, optional
            The maximum time to wait for a requested feature impact job to complete before erroring
        **kwargs
            Arbitrary keyword arguments passed to
            :meth:`request_feature_impact <datarobot.models.Model.request_feature_impact>`.

        Returns
        -------
         feature_impacts : list or dict
            The feature impact data. See
            :meth:`get_feature_impact <datarobot.models.Model.get_feature_impact>` for the exact
            schema.
        """
        try:
            feature_impact_job = self.request_feature_impact(**kwargs)
        except JobAlreadyRequested as e:
            # If already requested it may be still running. Check and get the job id in that case.
            qid = e.json["jobId"]
            if qid is None:
                # There are rare cases, when existing (old) job can not be retrieved.
                # Last resort: optimistically try to return an existing result.
                return self.get_feature_impact(**kwargs)

            from .job import FeatureImpactJob

            with_metadata = kwargs.get("with_metadata", False)
            feature_impact_job = FeatureImpactJob.get(
                self.project_id, qid, with_metadata=with_metadata
            )

        return feature_impact_job.get_result_when_complete(max_wait=max_wait)

    def _get_feature_effect_metadata_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_model_url() + "featureEffectsMetadata/"

    def get_feature_effect_metadata(self):
        """
        Retrieve Feature Effects metadata. Response contains status and available model sources.

        * Feature Fit for the `training` partition is always available, with the exception of older
          projects that only supported Feature Fit for `validation`.

        * When a model is trained into `validation` or `holdout` without stacked predictions
          (i.e., no out-of-sample predictions in those partitions),
          Feature Effects is not available for `validation` or `holdout`.

        * Feature Effects for `holdout` is not available when holdout was not unlocked for
          the project.

        Use `source` to retrieve Feature Effects, selecting one of the provided sources.

        Returns
        -------
        feature_effect_metadata: FeatureEffectMetadata

        """
        fe_metadata_url = self._get_feature_effect_metadata_url()
        server_data = self._client.get(fe_metadata_url).json()
        return FeatureEffectMetadata.from_server_data(server_data)

    def _get_feature_fit_metadata_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_model_url() + "featureFitMetadata/"

    def get_feature_fit_metadata(self):
        """
         Retrieve Feature Fit metadata. Response contains status and available model sources.

        * Feature Fit of `training` is always available
          (except for the old project which supports only Feature Fit for `validation`).

        * When a model is trained into `validation` or `holdout` without stacked prediction
          (e.g. no out-of-sample prediction in `validation` or `holdout`),
          Feature Fit is not available for `validation` or `holdout`.

        * Feature Fit for `holdout` is not available when there is no holdout configured for
          the project.

         `source` is expected parameter to retrieve Feature Fit. One of provided sources
         shall be used.

         Returns
         -------
         feature_effect_metadata: FeatureFitMetadata

        """
        ff_metadata_url = self._get_feature_fit_metadata_url()
        server_data = self._client.get(ff_metadata_url).json()
        return FeatureFitMetadata.from_server_data(server_data)

    def _get_feature_effect_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_model_url() + "featureEffects/"

    def request_feature_effect(self, row_count=None):
        """
        Request feature effects to be computed for the model.

        See :meth:`get_feature_effect <datarobot.models.Model.get_feature_effect>` for more
        information on the result of the job.

        Parameters
        ----------
        row_count : int
            (New in version v2.21) The sample size to use for Feature Impact computation.
            Minimum is 10 rows. Maximum is 100000 rows or the training sample size of the model,
            whichever is less.

        Returns
        -------
         job : Job
            A Job representing the feature effect computation. To get the completed feature effect
            data, use `job.get_result` or `job.get_result_when_complete`.

        Raises
        ------
        JobAlreadyRequested (422)
            If the feature effect have already been requested.
        """
        from .job import Job

        route = self._get_feature_effect_url()
        response = self._client.post(route, data={"row_count": row_count})
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def request_feature_effects_multiclass(
        self, row_count=None, top_n_features=None, features=None,
    ):
        """
        Request Feature Effects computation for the multiclass model.

        See :meth:`get_feature_effect <datarobot.models.Model.get_feature_effects_multiclass>` for
        more information on the result of the job.

        Parameters
        ----------
        row_count : int
            The number of rows from dataset to use for Feature Impact calculation.
        top_n_features : int or None
            Number of top features (ranked by feature impact) used to calculate Feature Effects.
        features : list or None
            The list of features used to calculate Feature Effects.

        Returns
        -------
         job : Job
            A Job representing Feature Effect computation. To get the completed Feature Effect
            data, use `job.get_result` or `job.get_result_when_complete`.
        """
        return FeatureEffectsMulticlass.create(
            project_id=self.project_id,
            model_id=self.id,
            row_count=row_count,
            top_n_features=top_n_features,
            features=features,
        )

    def get_feature_effect(self, source, include_ice_plots=False):
        """
        Retrieve Feature Effects for the model.

        Feature Effects provides partial dependence and predicted vs actual values for top-500
        features ordered by feature impact score.

        The partial dependence shows marginal effect of a feature on the target variable after
        accounting for the average effects of all other predictive features. It indicates how,
        holding all other variables except the feature of interest as they were,
        the value of this feature affects your prediction.

        Requires that Feature Effects has already been computed with
        :meth:`request_feature_effect <datarobot.models.Model.request_feature_effect>`.

        See :meth:`get_feature_effect_metadata <datarobot.models.Model.get_feature_effect_metadata>`
        for retrieving information the availiable sources.

        Parameters
        ----------
        source : string
            The source Feature Effects are retrieved for.
        include_ice_plots: bool, optional
            Indicates whether Individual Conditional Expectation (ICE) plots should be returned.

        Returns
        -------
        feature_effects : FeatureEffects
           The feature effects data.

        Raises
        ------
        ClientError (404)
            If the feature effects have not been computed or source is not valid value.
        """
        params = {"source": source, "includeIcePlots": include_ice_plots}
        fe_url = self._get_feature_effect_url()
        server_data = self._client.get(fe_url, params=params).json()
        return FeatureEffects.from_server_data(server_data)

    def get_feature_effects_multiclass(self, source="training", class_=None):
        """
        Retrieve Feature Effects for the multiclass model.

        Feature Effects provide partial dependence and predicted vs actual values for top-500
        features ordered by feature impact score.

        The partial dependence shows marginal effect of a feature on the target variable after
        accounting for the average effects of all other predictive features. It indicates how,
        holding all other variables except the feature of interest as they were,
        the value of this feature affects your prediction.

        Requires that Feature Effects has already been computed with
        :meth:`request_feature_effect <datarobot.models.Model.request_feature_effect>`.

        See :meth:`get_feature_effect_metadata <datarobot.models.Model.get_feature_effect_metadata>`
        for retrieving information the availiable sources.

        Parameters
        ----------
        source : str
            The source Feature Effects are retrieved for.
        class_ : str or None
            The class name Feature Effects are retrieved for.

        Returns
        -------
        list
           The list of multiclass feature effects.

        Raises
        ------
        ClientError (404)
            If Feature Effects have not been computed or source is not valid value.
        """
        return FeatureEffectsMulticlass.get(
            project_id=self.project_id, model_id=self.id, source=source, class_=class_
        )

    def get_or_request_feature_effects_multiclass(
        self,
        source,
        top_n_features=None,
        features=None,
        row_count=None,
        class_=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Feature Effects for the multiclass model, requesting a job if it hasn't been run
        previously.

        Parameters
        ----------
        source : string
            The source Feature Effects retrieve for.
        class_ : str or None
            The class name Feature Effects retrieve for.
        row_count : int
            The number of rows from dataset to use for Feature Impact calculation.
        top_n_features : int or None
            Number of top features (ranked by Feature Impact) used to calculate Feature Effects.
        features : list or None
            The list of features used to calculate Feature Effects.
        max_wait : int, optional
            The maximum time to wait for a requested Feature Effects job to complete before
            erroring.

        Returns
        -------
        feature_effects : list of FeatureEffectsMulticlass
           The list of multiclass feature effects data.
        """
        try:
            feature_effects = self.get_feature_effects_multiclass(source=source, class_=class_)
        except ClientError as e:
            if e.status_code == 404 and e.json.get("message") == "No data found for the model.":
                feature_effect_job = self.request_feature_effects_multiclass(
                    row_count=row_count, top_n_features=top_n_features, features=features,
                )
                params = {"source": source}
                if class_:
                    params["class"] = class_
                feature_effects = feature_effect_job.get_result_when_complete(
                    max_wait=max_wait, params=params
                )
            else:
                raise e

        return feature_effects

    def get_or_request_feature_effect(self, source, max_wait=DEFAULT_MAX_WAIT, row_count=None):
        """
        Retrieve feature effect for the model, requesting a job if it hasn't been run previously

        See :meth:`get_feature_effect_metadata \
        <datarobot.models.Model.get_feature_effect_metadata>`
        for retrieving information of source.

        Parameters
        ----------
        max_wait : int, optional
            The maximum time to wait for a requested feature effect job to complete before erroring
        row_count : int, optional
            (New in version v2.21) The sample size to use for Feature Impact computation.
            Minimum is 10 rows. Maximum is 100000 rows or the training sample size of the model,
            whichever is less.

        source : string
            The source Feature Effects are retrieved for.

        Returns
        -------
        feature_effects : FeatureEffects
           The feature effects data.
        """
        try:
            feature_effect_job = self.request_feature_effect(row_count=row_count)
        except JobAlreadyRequested as e:
            # if already requested it may be still running
            # check and get the jobid in that case
            qid = e.json["jobId"]
            from .job import Job

            feature_effect_job = Job.get(self.project_id, qid)

        params = {"source": source}
        return feature_effect_job.get_result_when_complete(max_wait=max_wait, params=params)

    def _get_feature_fit_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_model_url() + "featureFit/"

    def request_feature_fit(self):
        """
        Request feature fit to be computed for the model.

        See :meth:`get_feature_effect <datarobot.models.Model.get_feature_fit>` for more
        information on the result of the job.

        Returns
        -------
         job : Job
            A Job representing the feature fit computation. To get the completed feature fit
            data, use `job.get_result` or `job.get_result_when_complete`.

        Raises
        ------
        JobAlreadyRequested (422)
            If the feature effect have already been requested.
        """
        from .job import Job

        route = self._get_feature_fit_url()
        response = self._client.post(route)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def get_feature_fit(self, source, include_ice_plots=False):
        """
        Retrieve Feature Fit for the model.

        Feature Fit provides partial dependence and predicted vs actual values for top-500
        features ordered by feature importance score.

        The partial dependence shows marginal effect of a feature on the target variable after
        accounting for the average effects of all other predictive features. It indicates how,
        holding all other variables except the feature of interest as they were,
        the value of this feature affects your prediction.

        Requires that Feature Fit has already been computed with
        :meth:`request_feature_effect <datarobot.models.Model.request_feature_fit>`.

        See :meth:`get_feature_fit_metadata <datarobot.models.Model.get_feature_fit_metadata>`
        for retrieving information the availiable sources.

        Parameters
        ----------
        source : string
            The source Feature Fit are retrieved for.
            One value of [FeatureFitMetadata.sources].
        include_ice_plots: bool, optional
            Indicates whether Individual Conditional Expectation (ICE) plots should be returned.

        Returns
        -------
        feature_fit : FeatureFit
           The feature fit data.

        Raises
        ------
        ClientError (404)
            If the feature fit have not been computed or source is not valid value.
        """
        params = {"source": source, "includeIcePlots": include_ice_plots}
        fe_url = self._get_feature_fit_url()
        server_data = self._client.get(fe_url, params=params).json()
        return FeatureFit.from_server_data(server_data)

    def get_or_request_feature_fit(self, source, max_wait=DEFAULT_MAX_WAIT):
        """
        Retrieve feature fit for the model, requesting a job if it hasn't been run previously

        See :meth:`get_feature_fit_metadata \
        <datarobot.models.Model.get_feature_fit_metadata>`
        for retrieving information of source.

        Parameters
        ----------
        max_wait : int, optional
            The maximum time to wait for a requested feature fit job to complete before erroring

        source : string
            The source Feature Fit are retrieved for.
            One value of [FeatureFitMetadata.sources].

        Returns
        -------
        feature_effects : FeatureFit
           The feature fit data.
        """
        try:
            feature_fit_job = self.request_feature_fit()
        except JobAlreadyRequested as e:
            # if already requested it may be still running
            # check and get the jobid in that case
            qid = e.json["jobId"]
            from .job import Job

            feature_fit_job = Job.get(self.project_id, qid)

        params = {"source": source}
        return feature_fit_job.get_result_when_complete(max_wait=max_wait, params=params)

    def get_prime_eligibility(self):
        """Check if this model can be approximated with DataRobot Prime

        Returns
        -------
        prime_eligibility : dict
            a dict indicating whether a model can be approximated with DataRobot Prime
            (key `can_make_prime`) and why it may be ineligible (key `message`)
        """
        converter = t.Dict(
            {
                t.Key("can_make_prime"): t.Bool(),
                t.Key("message"): String(),
                t.Key("message_id"): Int(),
            }
        ).allow_extra("*")
        url = "projects/{}/models/{}/primeInfo/".format(self.project_id, self.id)
        response_data = from_api(self._client.get(url).json())
        safe_data = converter.check(response_data)
        return_keys = ["can_make_prime", "message"]
        return {key: safe_data[key] for key in return_keys}

    def request_approximation(self):
        """Request an approximation of this model using DataRobot Prime

        This will create several rulesets that could be used to approximate this model.  After
        comparing their scores and rule counts, the code used in the approximation can be downloaded
        and run locally.

        Returns
        -------
        job : Job
            the job generating the rulesets
        """
        from .job import Job

        url = "projects/{}/models/{}/primeRulesets/".format(self.project_id, self.id)
        response = self._client.post(url)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def get_rulesets(self):
        """List the rulesets approximating this model generated by DataRobot Prime

        If this model hasn't been approximated yet, will return an empty list.  Note that these
        are rulesets approximating this model, not rulesets used to construct this model.

        Returns
        -------
        rulesets : list of Ruleset
        """
        url = "projects/{}/models/{}/primeRulesets/".format(self.project_id, self.id)
        response = self._client.get(url).json()
        return [Ruleset.from_server_data(data) for data in response]

    def download_export(self, filepath):
        """
        Download an exportable model file for use in an on-premise DataRobot standalone
        prediction environment.

        This function can only be used if model export is enabled, and will only be useful
        if you have an on-premise environment in which to import it.

        Parameters
        ----------
        filepath : str
            The path at which to save the exported model file.
        """
        url = "{}{}/export/".format(self._base_model_path, self.id)
        response = self._client.get(url)
        with open(filepath, mode="wb") as out_file:
            out_file.write(response.content)

    def request_transferable_export(self, prediction_intervals_size=None):
        """
        Request generation of an exportable model file for use in an on-premise DataRobot standalone
        prediction environment.

        This function can only be used if model export is enabled, and will only be useful
        if you have an on-premise environment in which to import it.

        This function does not download the exported file. Use download_export for that.

        Parameters
        ----------
        prediction_intervals_size : int, optional
            (New in v2.19) For :ref:`time series <time_series>` projects only.
            Represents the percentile to use for the size of the prediction intervals. Prediction
            intervals size must be between 1 and 100 (inclusive).

        Examples
        --------
        .. code-block:: python

            model = datarobot.Model.get('project-id', 'model-id')
            job = model.request_transferable_export()
            job.wait_for_completion()
            model.download_export('my_exported_model.drmodel')

            # Client must be configured to use standalone prediction server for import:
            datarobot.Client(token='my-token-at-standalone-server',
                             endpoint='standalone-server-url/api/v2')

            imported_model = datarobot.ImportedModel.create('my_exported_model.drmodel')

        """
        from .job import Job

        url = "modelExports/"
        payload = {"project_id": self.project_id, "model_id": self.id}
        if prediction_intervals_size:
            payload.update({"percentile": prediction_intervals_size})
        response = self._client.post(url, data=payload)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def request_frozen_model(self, sample_pct=None, training_row_count=None):
        """
        Train a new frozen model with parameters from this model

        .. note::

            This method only works if project the model belongs to is `not` datetime
            partitioned.  If it is, use ``request_frozen_datetime_model`` instead.

        Frozen models use the same tuning parameters as their parent model instead of independently
        optimizing them to allow efficiently retraining models on larger amounts of the training
        data.

        Parameters
        ----------
        sample_pct : float
            optional, the percentage of the dataset to use with the model.  If not provided, will
            use the value from this model.
        training_row_count : int
            (New in version v2.9) optional, the integer number of rows of the dataset to use with
            the model. Only one of `sample_pct` and `training_row_count` should be specified.

        Returns
        -------
        model_job : ModelJob
            the modeling job training a frozen model
        """
        from .modeljob import ModelJob

        url = "projects/{}/frozenModels/".format(self.project_id)
        data = {"model_id": self.id}

        if sample_pct:
            data["sample_pct"] = sample_pct
        if training_row_count:
            data["training_row_count"] = training_row_count

        response = self._client.post(url, data=data)
        job_id = get_id_from_response(response)
        return ModelJob.from_id(self.project_id, job_id)

    def request_frozen_datetime_model(
        self,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        time_window_sample_pct=None,
        sampling_method=None,
    ):
        """Train a new frozen model with parameters from this model.

        Requires that this model belongs to a datetime partitioned project.  If it does not, an
        error will occur when submitting the job.

        Frozen models use the same tuning parameters as their parent model instead of independently
        optimizing them to allow efficiently retraining models on larger amounts of the training
        data.

        In addition of training_row_count and training_duration, frozen datetime models may be
        trained on an exact date range.  Only one of training_row_count, training_duration, or
        training_start_date and training_end_date should be specified.

        Models specified using training_start_date and training_end_date are the only ones that can
        be trained into the holdout data (once the holdout is unlocked).

        All durations should be specified with a duration string such as those returned
        by the :meth:`partitioning_methods.construct_duration_string
        <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
        Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
        for more information on duration strings.

        Parameters
        ----------
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            training_duration may not be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, training_row_count may not be specified.
        training_start_date : datetime.datetime, optional
            the start date of the data to train to model on.  Only rows occurring at or after
            this datetime will be used.  If training_start_date is specified, training_end_date
            must also be specified.
        training_end_date : datetime.datetime, optional
            the end date of the data to train the model on.  Only rows occurring strictly before
            this datetime will be used.  If training_end_date is specified, training_start_date
            must also be specified.
        time_window_sample_pct : int, optional
            may only be specified when the requested model is a time window (e.g. duration or start
            and end dates).  An integer between 1 and 99 indicating the percentage to sample by
            within the window.  The points kept are determined by a random uniform sample.
            If specified, training_duration must be specified otherwise, the number of rows used
            to train the model and evaluate backtest scores and an error will occur.
        sampling_method : str, optional
            (New in version v2.23) defines the way training data is selected. Can be either
            ``random`` or ``latest``.  In combination with ``training_row_count`` defines how rows
            are selected from backtest (``latest`` by default).  When training data is defined using
            time range (``training_duration`` or ``use_project_settings``) this setting changes the
            way ``time_window_sample_pct`` is applied (``random`` by default).  Applicable to OTV
            projects only.

        Returns
        -------
        model_job : ModelJob
            the modeling job training a frozen model
        """
        from .modeljob import ModelJob

        if training_start_date is not None and not isinstance(training_start_date, datetime):
            raise ValueError("expected training_start_date to be a datetime.datetime")
        if training_end_date is not None and not isinstance(training_end_date, datetime):
            raise ValueError("expected training_end_date to be a datetime.datetime")
        url = "projects/{}/frozenDatetimeModels/".format(self.project_id)
        payload = {
            "model_id": self.id,
            "training_row_count": training_row_count,
            "training_duration": training_duration,
            "training_start_date": training_start_date,
            "training_end_date": training_end_date,
            "time_window_sample_pct": time_window_sample_pct,
        }
        if sampling_method:
            payload["sampling_method"] = sampling_method
        response = self._client.post(url, data=payload)
        return ModelJob.from_id(self.project_id, get_id_from_response(response))

    def get_parameters(self):
        """Retrieve model parameters.

        Returns
        -------
        ModelParameters
            Model parameters for this model.
        """
        return ModelParameters.get(self.project_id, self.id)

    def _get_insight(self, url_template, source, insight_type, fallback_to_parent_insights=False):
        """
        Retrieve insight data

        Parameters
        ----------
        url_template: str
            Format string for the insight url
        insight_type: str
            Name of insight type.  Used in warning messages.
        source: str
            Data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.
        fallback_to_parent_insights : bool
            Optional, if True, this will attempt to return insight data for this
            model's parent if the insight is not available for this model and the model has a
            defined parent model. If omitted or False, or there is no parent model, will not
            attempt to return insight data from this model's parent.

        Returns
        -------
        Model Insight Data

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url = url_template.format(self.project_id, self.id, source)
        source_model_id = self.id
        try:
            response_data = self._client.get(url).json()
        except ClientError as e:
            if e.status_code == 404 and fallback_to_parent_insights and self.is_frozen:
                frozen_model = FrozenModel.get(self.project_id, self.id)
                parent_model_id = frozen_model.parent_model_id
                source_model_id = parent_model_id
                url = url_template.format(self.project_id, parent_model_id, source)
                warning_message = (
                    "{} is not available for model {}. "
                    "Falling back to parent model {}.".format(
                        insight_type, self.id, parent_model_id
                    )
                )
                warnings.warn(warning_message, ParentModelInsightFallbackWarning, stacklevel=3)
                response_data = self._client.get(url).json()
            else:
                raise
        if insight_type == "Residuals Chart":
            response_data = self._format_residuals_chart(response_data)["charts"][0]

        response_data["source_model_id"] = source_model_id
        return response_data

    def _get_all_source_insight(
        self, url_template, insight_type, fallback_to_parent_insights=False
    ):
        """
        Retrieve insight data for all sources

        Parameters
        ----------
        url_template: str
            Format string for the insight url
        insight_type: str
            Name of insight type.  Used in warning messages.
        fallback_to_parent_insights : bool
            Optional, if True, this will return insight data for this
            model's parent for any source that is not available for this model, if this model
            has a defined parent model. If omitted or False, or this model has no parent,
            this will not attempt to retrieve any insight data from this model's parent.

        Returns
        -------
        List[insight data]
        """
        url = url_template.format(self.project_id, self.id)
        response_data = self._client.get(url).json()
        if insight_type == "Residuals Chart":
            response_data = self._format_residuals_chart(response_data)
        sources = []
        for chart in response_data["charts"]:
            chart["source_model_id"] = self.id
            sources.append(chart["source"])

        source_types = [
            CHART_DATA_SOURCE.VALIDATION,
            CHART_DATA_SOURCE.CROSSVALIDATION,
            CHART_DATA_SOURCE.HOLDOUT,
        ]
        if (
            fallback_to_parent_insights
            and self.is_frozen
            and any((source_type not in sources for source_type in source_types))
        ):
            frozen_model = FrozenModel.get(self.project_id, self.id)
            parent_model_id = frozen_model.parent_model_id
            url = url_template.format(self.project_id, parent_model_id)
            warning_message = (
                "{} is not available for all sources for model {}. "
                "Falling back to parent model {} for missing sources".format(
                    insight_type, self.id, parent_model_id
                )
            )
            warnings.warn(warning_message, ParentModelInsightFallbackWarning, stacklevel=3)
            parent_data = self._client.get(url).json()
            if insight_type == "Residuals Chart":
                parent_data = self._format_residuals_chart(parent_data)
            for chart in parent_data["charts"]:
                if chart["source"] not in sources:
                    chart["source_model_id"] = parent_model_id
                    response_data["charts"].append(chart)

        return response_data

    def _format_residuals_chart(self, response_data):
        """Reformat the residuals chart API data to match the standard used by
        the Lift and ROC charts
        """
        if list(response_data) == ["charts"]:
            # already been reformatted, so nothing to do
            return response_data
        reformatted = {
            "charts": [],
        }
        if list(response_data) == ["residuals"]:
            response_data = response_data["residuals"]
        for data_source, data in response_data.items():
            reformatted["charts"].append(dict(source=data_source, **data))
        return reformatted

    def get_lift_chart(self, source, fallback_to_parent_insights=False):
        """Retrieve the model Lift chart for the specified source.

        Parameters
        ----------
        source : str
            Lift chart data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.
            (New in version v2.23) For time series and OTV models, also accepts values `backtest_2`,
            `backtest_3`, ..., up to the number of backtests in the model.
        fallback_to_parent_insights : bool
            (New in version v2.14) Optional, if True, this will return lift chart data for this
            model's parent if the lift chart is not available for this model and the model has a
            defined parent model. If omitted or False, or there is no parent model, will not
            attempt to return insight data from this model's parent.

        Returns
        -------
        LiftChart
            Model lift chart data

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/liftChart/{}/"
        response_data = self._get_insight(
            url_template,
            source,
            "Lift Chart",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )
        return LiftChart.from_server_data(response_data)

    def get_all_lift_charts(self, fallback_to_parent_insights=False):
        """Retrieve a list of all Lift charts available for the model.

        Parameters
        ----------
        fallback_to_parent_insights : bool
            (New in version v2.14) Optional, if True, this will return lift chart data for this
            model's parent for any source that is not available for this model and if this model
            has a defined parent model. If omitted or False, or this model has no parent,
            this will not attempt to retrieve any data from this model's parent.

        Returns
        -------
        list of LiftChart
            Data for all available model lift charts.

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/liftChart/"
        response_data = self._get_all_source_insight(
            url_template, "Lift Chart", fallback_to_parent_insights=fallback_to_parent_insights
        )
        return [LiftChart.from_server_data(lc_data) for lc_data in response_data["charts"]]

    def get_multiclass_lift_chart(self, source, fallback_to_parent_insights=False):
        """Retrieve model Lift chart for the specified source.

        Parameters
        ----------
        source : str
            Lift chart data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.
        fallback_to_parent_insights : bool
            Optional, if True, this will return lift chart data for this
            model's parent if the lift chart is not available for this model and the model has a
            defined parent model. If omitted or False, or there is no parent model, will not
            attempt to return insight data from this model's parent.

        Returns
        -------
        list of LiftChart
            Model lift chart data for each saved target class

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/multiclassLiftChart/{}/"
        response_data = self._get_insight(
            url_template,
            source,
            "Multiclass Lift Chart",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )

        return [
            LiftChart.from_server_data(
                dict(
                    source=response_data["source"],
                    sourceModelId=response_data["source_model_id"],
                    **rec
                )
            )
            for rec in response_data["classBins"]
        ]

    def get_all_multiclass_lift_charts(self, fallback_to_parent_insights=False):
        """Retrieve a list of all Lift charts available for the model.

        Parameters
        ----------
        fallback_to_parent_insights : bool
            (New in version v2.14) Optional, if True, this will return lift chart data for this
            model's parent for any source that is not available for this model and if this model
            has a defined parent model. If omitted or False, or this model has no parent,
            this will not attempt to retrieve any data from this model's parent.

        Returns
        -------
        list of LiftChart
            Data for all available model lift charts.

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/multiclassLiftChart/"
        response_data = self._get_all_source_insight(
            url_template,
            "Multiclass Lift Chart",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )
        lift_charts = list()
        charts = response_data.get("charts") or []
        for chart in charts:
            for class_bin in chart["classBins"]:
                lift_chart = LiftChart.from_server_data(
                    dict(
                        source=chart["source"], sourceModelId=chart["source_model_id"], **class_bin
                    )
                )
                lift_charts.append(lift_chart)
        return lift_charts

    def get_multilabel_lift_charts(self, source, fallback_to_parent_insights=False):
        """Retrieve model Lift charts for the specified source.

        .. versionadded:: v2.24

        Parameters
        ----------
        source : str
            Lift chart data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.
        fallback_to_parent_insights : bool
            Optional, if True, this will return lift chart data for this
            model's parent if the lift chart is not available for this model and the model has a
            defined parent model. If omitted or False, or there is no parent model, will not
            attempt to return insight data from this model's parent.

        Returns
        -------
        list of LiftChart
            Model lift chart data for each saved target class

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/multilabelLiftCharts/{}/"
        response_data = self._get_insight(
            url_template,
            source,
            "Multilabel Lift Chart",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )

        lift_charts = []
        for bin in response_data["labelBins"]:
            lift_chart = LiftChart.from_server_data(
                dict(
                    source=response_data["source"],
                    sourceModelId=response_data["source_model_id"],
                    target_class=bin["label"],
                    bins=bin["bins"],
                )
            )
            lift_charts.append(lift_chart)
        return lift_charts

    def get_residuals_chart(self, source, fallback_to_parent_insights=False):
        """ Retrieve model residuals chart for the specified source.

        Parameters
        ----------
        source : str
            Residuals chart data source. Check datarobot.enums.CHART_DATA_SOURCE for possible
            values.
        fallback_to_parent_insights : bool
            Optional, if True, this will return residuals chart data for this model's parent if
            the residuals chart is not available for this model and the model has a defined parent
            model. If omitted or False, or there is no parent model, will not attempt to return
            residuals data from this model's parent.

        Returns
        -------
        ResidualsChart
            Model residuals chart data

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/residuals/{}/"
        response_data = self._get_insight(
            url_template,
            source,
            "Residuals Chart",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )
        return ResidualsChart.from_server_data(response_data)

    def get_all_residuals_charts(self, fallback_to_parent_insights=False):
        """Retrieve a list of all Lift charts available for the model.

        Parameters
        ----------
        fallback_to_parent_insights : bool
            Optional, if True, this will return residuals chart data for this model's parent
            for any source that is not available for this model and if this model has a
            defined parent model. If omitted or False, or this model has no parent, this will
            not attempt to retrieve any data from this model's parent.

        Returns
        -------
        list of ResidualsChart
            Data for all available model residuals charts.
        """
        url_template = "projects/{}/models/{}/residuals/"
        response_data = self._get_all_source_insight(
            url_template,
            "Residuals Chart",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )
        return [ResidualsChart.from_server_data(lc_data) for lc_data in response_data["charts"]]

    def get_pareto_front(self):
        """Retrieve the Pareto Front for a Eureqa model.

        This method is only supported for Eureqa models.

        Returns
        -------
        ParetoFront
            Model ParetoFront data
        """
        url = "projects/{}/eureqaModels/{}/".format(self.project_id, self.id)
        response_data = self._client.get(url).json()
        return ParetoFront.from_server_data(response_data)

    def get_confusion_chart(self, source, fallback_to_parent_insights=False):
        """Retrieve them model's confusion matrix for the specified source.

        Parameters
        ----------
        source : str
           Confusion chart source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.
        fallback_to_parent_insights : bool
            (New in version v2.14) Optional, if True, this will return confusion chart data for
            this model's parent if the confusion chart is not available for this model and the
            defined parent model. If omitted or False, or there is no parent model, will not
            attempt to return insight data from this model's parent.

        Returns
        -------
        ConfusionChart
            Model ConfusionChart data

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/confusionCharts/{}/"
        response_data = self._get_insight(
            url_template,
            source,
            "Confusion Chart",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )
        self._fix_confusion_chart_classes([response_data])
        return ConfusionChart.from_server_data(response_data)

    def get_all_confusion_charts(self, fallback_to_parent_insights=False):
        """Retrieve a list of all confusion matrices available for the model.

        Parameters
        ----------
        fallback_to_parent_insights : bool
            (New in version v2.14) Optional, if True, this will return confusion chart data for
            this model's parent for any source that is not available for this model and if this
            has a defined parent model. If omitted or False, or this model has no parent,
            this will not attempt to retrieve any data from this model's parent.

        Returns
        -------
        list of ConfusionChart
            Data for all available confusion charts for model.
        """
        url_template = "projects/{}/models/{}/confusionCharts/"
        response_data = self._get_all_source_insight(
            url_template, "Confusion Chart", fallback_to_parent_insights=fallback_to_parent_insights
        )
        self._fix_confusion_chart_classes(response_data["charts"])
        return [ConfusionChart.from_server_data(cc_data) for cc_data in response_data["charts"]]

    def _fix_confusion_chart_classes(self, charts_to_fix):
        """Replace the deprecated classes field.

        Since the confusion chart is now "paginated" classes should be taken from the metadata.
        This mutates the dictionaries to not rely on the deprecated key.

        Parameters
        ----------
        charts_to_fix : list of dict
            list of confusion chart data to be mutated
        """
        url_template = "projects/{}/models/{}/confusionCharts/{}/metadata/"
        for chart in charts_to_fix:
            model_id = chart.get("source_model_id", self.id)
            metadata = self._client.get(
                url_template.format(self.project_id, model_id, chart["source"])
            ).json()
            chart["data"]["classes"] = metadata["classNames"]

    def get_roc_curve(self, source, fallback_to_parent_insights=False):
        """Retrieve the ROC curve for the specified source.

        Parameters
        ----------
        source : str
            ROC curve data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.
            (New in version v2.23) For time series and OTV models, also accepts values `backtest_2`,
            `backtest_3`, ..., up to the number of backtests in the model.
        fallback_to_parent_insights : bool
            (New in version v2.14) Optional, if True, this will return ROC curve data for this
            model's parent if the ROC curve is not available for this model and the model has a
            defined parent model. If omitted or False, or there is no parent model, will not
            attempt to return data from this model's parent.

        Returns
        -------
        RocCurve
            Model ROC curve data

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/rocCurve/{}/"
        response_data = self._get_insight(
            url_template,
            source,
            "ROC Curve",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )
        return RocCurve.from_server_data(response_data)

    def get_all_roc_curves(self, fallback_to_parent_insights=False):
        """Retrieve a list of all ROC curves available for the model.

        Parameters
        ----------
        fallback_to_parent_insights : bool
            (New in version v2.14) Optional, if True, this will return ROC curve data for this
            model's parent for any source that is not available for this model and if this model
            has a defined parent model. If omitted or False, or this model has no parent,
            this will not attempt to retrieve any data from this model's parent.

        Returns
        -------
        list of RocCurve
            Data for all available model ROC curves.
        """
        url_template = "projects/{}/models/{}/rocCurve/"
        response_data = self._get_all_source_insight(
            url_template, "ROC Curve", fallback_to_parent_insights=fallback_to_parent_insights
        )
        return [RocCurve.from_server_data(lc_data) for lc_data in response_data["charts"]]

    def get_labelwise_roc_curves(self, source, fallback_to_parent_insights=False):
        """Retrieve a list of LabelwiseRocCurve instances for the given source and all labels.

        .. versionadded:: v2.24

        Parameters
        ----------
        source : str
            ROC curve data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.
        fallback_to_parent_insights : bool
            Optional, if True, this will return ROC curve data for this
            model's parent if the ROC curve is not available for this model and the model has a
            defined parent model. If omitted or False, or there is no parent model, will not
            attempt to return data from this model's parent.

        Returns
        -------
        list of :class:`LabelwiseRocCurve <datarobot.models.roc_curve.LabelwiseRocCurve>`
            Labelwise ROC Curve instances for ``source`` and all labels

        Raises
        ------
        ClientError
            If the insight is not available for this model
        """
        url_template = "projects/{}/models/{}/labelwiseRocCurves/{}/"
        response_data = self._get_insight(
            url_template,
            source,
            "Labelwise ROC Curve",
            fallback_to_parent_insights=fallback_to_parent_insights,
        )
        labelwise_roc_curves = []
        source_model_id = response_data["source_model_id"]
        for chart in response_data["charts"]:
            chart["source_model_id"] = source_model_id
            labelwise_roc_curve = LabelwiseRocCurve.from_server_data(chart)
            labelwise_roc_curves.append(labelwise_roc_curve)
        return labelwise_roc_curves

    def get_word_cloud(self, exclude_stop_words=False):
        """Retrieve word cloud data for the model.

        Parameters
        ----------
        exclude_stop_words : bool, optional
            Set to True if you want stopwords filtered out of response.

        Returns
        -------
        WordCloud
            Word cloud data for the model.
        """
        url = "projects/{}/models/{}/wordCloud/?excludeStopWords={}".format(
            self.project_id, self.id, "true" if exclude_stop_words else "false"
        )
        response_data = self._client.get(url).json()
        return WordCloud.from_server_data(response_data)

    def download_scoring_code(self, file_name, source_code=False):
        """Download the Scoring Code JAR.

        Parameters
        ----------
        file_name : str
            File path where scoring code will be saved.
        source_code : bool, optional
            Set to True to download source code archive.
            It will not be executable.
        """
        url = "projects/{}/models/{}/scoringCode/?sourceCode={}".format(
            self.project_id, self.id, "true" if source_code else "false"
        )
        response = self._client.get(url, stream=True)
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    def get_model_blueprint_documents(self):
        """Get documentation for tasks used in this model.

        Returns
        -------
        list of BlueprintTaskDocument
            All documents available for the model.
        """
        url = "projects/{}/models/{}/blueprintDocs/".format(self.project_id, self.id)
        return [BlueprintTaskDocument.from_server_data(data) for data in self._server_data(url)]

    def get_model_blueprint_chart(self):
        """Retrieve a diagram that can be used to understand
        data flow in the blueprint.

        Returns
        -------
        ModelBlueprintChart
            The queried model blueprint chart.
        """
        return ModelBlueprintChart.get(self.project_id, self.id)

    def get_missing_report_info(self):
        """Retrieve a report on missing training data that can be used to understand missing
        values treatment in the model. The report consists of missing values resolutions for
        features numeric or categorical features that were part of building the model.

        Returns
        -------
        An iterable of MissingReportPerFeature
            The queried model missing report, sorted by missing count (DESCENDING order).
        """
        return MissingValuesReport.get(self.project_id, self.id)

    def get_frozen_child_models(self):
        """Retrieve the IDs for all models that are frozen from this model.

        Returns
        -------
        A list of Models
        """
        from datarobot.models.project import Project

        parent_id = self.id
        proj = Project.get(self.project_id)
        return [model for model in proj.get_frozen_models() if model.parent_model_id == parent_id]

    def request_training_predictions(
        self, data_subset, explanation_algorithm=None, max_explanations=None
    ):
        """Start a job to build training predictions

        Parameters
        ----------
        data_subset : str
            data set definition to build predictions on.
            Choices are:

                - `dr.enums.DATA_SUBSET.ALL` or string `all` for all data available. Not valid for
                    models in datetime partitioned projects
                - `dr.enums.DATA_SUBSET.VALIDATION_AND_HOLDOUT` or string `validationAndHoldout` for
                    all data except training set. Not valid for models in datetime partitioned
                    projects
                - `dr.enums.DATA_SUBSET.HOLDOUT` or string `holdout` for holdout data set only
                - `dr.enums.DATA_SUBSET.ALL_BACKTESTS` or string `allBacktests` for downloading
                    the predictions for all backtest validation folds. Requires the model to have
                    successfully scored all backtests. Datetime partitioned projects only.
        explanation_algorithm : dr.enums.EXPLANATIONS_ALGORITHM
            (New in v2.21) Optional. If set to `dr.enums.EXPLANATIONS_ALGORITHM.SHAP`, the response
            will include prediction explanations based on the SHAP explainer (SHapley Additive
            exPlanations). Defaults to `None` (no prediction explanations).
        max_explanations : int
            (New in v2.21) Optional. Specifies the maximum number of explanation values that should
            be returned for each row, ordered by absolute value, greatest to least. In the case of
            `dr.enums.EXPLANATIONS_ALGORITHM.SHAP`:  If not set, explanations are returned for all
            features. If the number of features is greater than the ``max_explanations``, the sum of
            remaining values will also be returned as ``shap_remaining_total``. Max 100. Defaults to
            null for datasets narrower than 100 columns, defaults to 100 for datasets wider than 100
            columns. Is ignored if ``explanation_algorithm`` is not set.

        Returns
        -------
        Job
            an instance of created async job
        """
        from .job import TrainingPredictionsJob

        path = TrainingPredictions.build_path(self.project_id)
        payload = {
            "model_id": self.id,
            "data_subset": data_subset,
        }
        if explanation_algorithm:
            payload["explanation_algorithm"] = explanation_algorithm
            if max_explanations:
                payload["max_explanations"] = max_explanations
        response = self._client.post(path, data=payload)
        job_id = get_id_from_response(response)

        return TrainingPredictionsJob.get(
            self.project_id, job_id, model_id=self.id, data_subset=data_subset,
        )

    def cross_validate(self):
        """Run cross validation on the model.

        .. note:: To perform Cross Validation on a new model with new parameters,
            use ``train`` instead.

        Returns
        -------
        ModelJob
            The created job to build the model
        """
        from .modeljob import ModelJob

        url = "projects/{}/models/{}/crossValidation/".format(self.project_id, self.id)
        response = self._client.post(url)

        job_id = get_id_from_response(response)

        return ModelJob.get(self.project_id, job_id)

    def get_cross_validation_scores(self, partition=None, metric=None):
        """Return a dictionary, keyed by metric, showing cross validation
        scores per partition.

        Cross Validation should already have been performed using
        :meth:`cross_validate <datarobot.models.Model.cross_validate>` or
        :meth:`train <datarobot.models.Model.train>`.

        .. note:: Models that computed cross validation before this feature was added will need
           to be deleted and retrained before this method can be used.

        Parameters
        ----------
        partition : float
            optional, the id of the partition (1,2,3.0,4.0,etc...) to filter results by
            can be a whole number positive integer or float value.
        metric: unicode
            optional name of the metric to filter to resulting cross validation scores by

        Returns
        -------
        cross_validation_scores: dict
            A dictionary keyed by metric showing cross validation scores per
            partition.
        """
        url = "projects/{}/models/{}/crossValidationScores/".format(self.project_id, self.id)
        querystring = []
        if partition:
            querystring.append("partition={}".format(partition))
        if metric:
            querystring.append("metric={}".format(metric))
        if querystring:
            url += "?" + "&".join(querystring)

        response = self._client.get(url)
        return response.json()

    def advanced_tune(self, params, description=None):
        """Generate a new model with the specified advanced-tuning parameters

        As of v2.17, all models other than blenders, open source, prime, scaleout, baseline and
        user-created support Advanced Tuning.

        Parameters
        ----------
        params : dict
            Mapping of parameter ID to parameter value.
            The list of valid parameter IDs for a model can be found by calling
            `get_advanced_tuning_parameters()`.
            This endpoint does not need to include values for all parameters.  If a parameter
            is omitted, its `current_value` will be used.
        description : unicode
            Human-readable string describing the newly advanced-tuned model

        Returns
        -------
        ModelJob
            The created job to build the model
        """
        from .modeljob import ModelJob

        params_list = [
            {"parameterId": parameterID, "value": value} for parameterID, value in params.items()
        ]

        payload = {"tuningDescription": description, "tuningParameters": params_list}

        url = "projects/{}/models/{}/advancedTuning/".format(self.project_id, self.id)
        response = self._client.post(url, data=payload)

        job_id = get_id_from_response(response)

        return ModelJob.get(self.project_id, job_id)

    ##########
    # Advanced Tuning validation
    ##########
    _FlatValue = Int | t.Float | String(allow_blank=True) | t.Bool | t.Null

    _Value = _FlatValue | t.List(_FlatValue) | t.List(t.List(_FlatValue))

    _SelectConstraint = t.Dict({t.Key("values"): t.List(_FlatValue)}).ignore_extra("*")

    _ASCIIConstraint = t.Dict({}).ignore_extra("*")

    _UnicodeConstraint = t.Dict({}).ignore_extra("*")

    _IntConstraint = t.Dict(
        {t.Key("min"): Int, t.Key("max"): Int, t.Key("supports_grid_search"): t.Bool}
    ).ignore_extra("*")

    _FloatConstraint = t.Dict(
        {t.Key("min"): t.Float, t.Key("max"): t.Float, t.Key("supports_grid_search"): t.Bool}
    ).ignore_extra("*")

    _IntListConstraint = t.Dict(
        {
            t.Key("min_length"): Int,
            t.Key("max_length"): Int,
            t.Key("min_val"): Int,
            t.Key("max_val"): Int,
            t.Key("supports_grid_search"): t.Bool,
        }
    ).ignore_extra("*")

    _FloatListConstraint = t.Dict(
        {
            t.Key("min_length"): Int,
            t.Key("max_length"): Int,
            t.Key("min_val"): t.Float,
            t.Key("max_val"): t.Float,
            t.Key("supports_grid_search"): t.Bool,
        }
    ).ignore_extra("*")

    _Constraints = t.Dict(
        {
            t.Key("select", optional=True): _SelectConstraint,
            t.Key("ascii", optional=True): _ASCIIConstraint,
            t.Key("unicode", optional=True): _UnicodeConstraint,
            t.Key("int", optional=True): _IntConstraint,
            t.Key("float", optional=True): _FloatConstraint,
            t.Key("int_list", optional=True): _IntListConstraint,
            t.Key("float_list", optional=True): _FloatListConstraint,
        }
    ).ignore_extra("*")

    _TuningParameters = t.Dict(
        {
            t.Key("parameter_name"): String(),
            t.Key("parameter_id"): String,
            t.Key("default_value"): _Value,
            t.Key("current_value"): _Value,
            t.Key("task_name"): String,
            t.Key("constraints"): _Constraints,
        }
    ).ignore_extra("*")

    _TuningResponse = t.Dict(
        {
            t.Key("tuning_description", default=None): String(allow_blank=True) | t.Null,
            t.Key("tuning_parameters"): t.List(_TuningParameters),
        }
    ).ignore_extra("*")

    def get_advanced_tuning_parameters(self):
        """Get the advanced-tuning parameters available for this model.

        As of v2.17, all models other than blenders, open source, prime, scaleout, baseline and
        user-created support Advanced Tuning.

        Returns
        -------
        dict
            A dictionary describing the advanced-tuning parameters for the current model.
            There are two top-level keys, `tuningDescription` and `tuningParameters`.

            `tuningDescription` an optional value. If not `None`, then it indicates the
            user-specified description of this set of tuning parameter.

            `tuningParameters` is a list of a dicts, each has the following keys

            * parameterName : **(unicode)** name of the parameter (unique per task, see below)
            * parameterId : **(unicode)** opaque ID string uniquely identifying parameter
            * defaultValue : **(*)** default value of the parameter for the blueprint
            * currentValue : **(*)** value of the parameter that was used for this model
            * taskName : **(unicode)** name of the task that this parameter belongs to
            * constraints: **(dict)** see the notes below


        Notes
        -----
        The type of `defaultValue` and `currentValue` is defined by the `constraints` structure.
        It will be a string or numeric Python type.

        `constraints` is a dict with `at least one`, possibly more, of the following keys.
        The presence of a key indicates that the parameter may take on the specified type.
        (If a key is absent, this means that the parameter may not take on the specified type.)
        If a key on `constraints` is present, its value will be a dict containing
        all of the fields described below for that key.

        .. code-block:: python

            "constraints": {
                "select": {
                    "values": [<list(basestring or number) : possible values>]
                },
                "ascii": {},
                "unicode": {},
                "int": {
                    "min": <int : minimum valid value>,
                    "max": <int : maximum valid value>,
                    "supports_grid_search": <bool : True if Grid Search may be
                                                    requested for this param>
                },
                "float": {
                    "min": <float : minimum valid value>,
                    "max": <float : maximum valid value>,
                    "supports_grid_search": <bool : True if Grid Search may be
                                                    requested for this param>
                },
                "intList": {
                    "length": {
                    "min_length": <int : minimum valid length>,
                    "max_length": <int : maximum valid length>
                    "min_val": <int : minimum valid value>,
                    "max_val": <int : maximum valid value>
                    "supports_grid_search": <bool : True if Grid Search may be
                                                    requested for this param>
                },
                "floatList": {
                    "min_length": <int : minimum valid length>,
                    "max_length": <int : maximum valid length>
                    "min_val": <float : minimum valid value>,
                    "max_val": <float : maximum valid value>
                    "supports_grid_search": <bool : True if Grid Search may be
                                                    requested for this param>
                }
            }

        The keys have meaning as follows:

        * `select`:
          Rather than specifying a specific data type, if present, it indicates that the parameter
          is permitted to take on any of the specified values.  Listed values may be of any string
          or real (non-complex) numeric type.

        * `ascii`:
          The parameter may be a `unicode` object that encodes simple ASCII characters.
          (A-Z, a-z, 0-9, whitespace, and certain common symbols.)  In addition to listed
          constraints, ASCII keys currently may not contain either newlines or semicolons.

        * `unicode`:
          The parameter may be any Python `unicode` object.

        * `int`:
          The value may be an object of type `int` within the specified range (inclusive).
          Please note that the value will be passed around using the JSON format, and
          some JSON parsers have undefined behavior with integers outside of the range
          [-(2**53)+1, (2**53)-1].

        * `float`:
          The value may be an object of type `float` within the specified range (inclusive).

        * `intList`, `floatList`:
          The value may be a list of `int` or `float` objects, respectively, following constraints
          as specified respectively by the `int` and `float` types (above).

        Many parameters only specify one key under `constraints`.  If a parameter specifies multiple
        keys, the parameter may take on any value permitted by any key.
        """
        url = "projects/{}/models/{}/advancedTuning/parameters/".format(self.project_id, self.id)
        response = self._client.get(url)

        cleaned_response = from_api(response.json(), do_recursive=True, keep_null_keys=True)
        data = self._TuningResponse.check(cleaned_response)

        return data

    def start_advanced_tuning_session(self):
        """Start an Advanced Tuning session.  Returns an object that helps
        set up arguments for an Advanced Tuning model execution.

        As of v2.17, all models other than blenders, open source, prime, scaleout, baseline and
        user-created support Advanced Tuning.

        Returns
        -------
        AdvancedTuningSession
            Session for setting up and running Advanced Tuning on a model
        """
        return AdvancedTuningSession(self)

    def star_model(self):
        """Mark the model as starred.

        Model stars propagate to the web application and the API, and can be used to filter when
        listing models.
        """
        self._toggle_starred(True)

    def unstar_model(self):
        """Unmark the model as starred.

        Model stars propagate to the web application and the API, and can be used to filter when
        listing models.
        """
        self._toggle_starred(False)

    def _toggle_starred(self, is_starred):
        """Mark or unmark model instance as starred.

        Parameters
        ----------
        is_starred : bool
            Whether to mark the model as starred or unmark a previously set flag.
        """
        url = "projects/{}/models/{}/".format(self.project_id, self.id)
        self._client.patch(url, data={"is_starred": is_starred})
        self.is_starred = is_starred

    def set_prediction_threshold(self, threshold):
        """Set a custom prediction threshold for the model.

        May not be used once ``prediction_threshold_read_only`` is True for this model.

        Parameters
        ----------
        threshold : float
           only used for binary classification projects. The threshold to when deciding between
           the positive and negative classes when making predictions.  Should be between 0.0 and
           1.0 (inclusive).
        """
        url = "projects/{}/models/{}/".format(self.project_id, self.id)
        self._client.patch(url, data={"prediction_threshold": threshold})
        self.prediction_threshold = threshold

    def download_training_artifact(self, file_name):
        """Retrieve trained artifact(s) from a model containing one or more custom tasks.

        Artifact(s) will be downloaded to the specified local filepath.

        Parameters
        ----------
        file_name : str
            File path where trained model artifact(s) will be saved.
        """
        url = "projects/{}/models/{}/trainingArtifact/".format(self.project_id, self.id)
        response = self._client.get(url)
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    def request_fairness_insights(self, fairness_metrics_set=None):
        """
        Request fairness insights to be computed for the model.

        Parameters
        ----------
        fairness_metrics_set : str, optional
            Can be one of <datarobot.enums.FairnessMetricsSet>.
            The fairness metric used to calculate the fairness scores.

        Returns
        -------
        status_id : str
            A statusId of computation request.
        """
        route = urljoin(self._get_model_url(), "fairnessInsights/")
        data = {"fairness_metrics_set": fairness_metrics_set} if fairness_metrics_set else {}
        response = self._client.post(route, data)
        status_id = get_id_from_response(response)

        return status_id

    def get_fairness_insights(self, fairness_metrics_set=None, offset=0, limit=100):
        """
        Retrieve a list of Per Class Bias insights for the model.

        Parameters
        ----------
        fairness_metrics_set : str, optional
            Can be one of <datarobot.enums.FairnessMetricsSet>.
            The fairness metric used to calculate the fairness scores.
        offset : int, optional
            Number of items to skip.
        limit : int, optional
            Number of items to return.

        Returns
        -------
        json
        """
        query_params = "?offset={}&limit={}".format(offset, limit)
        if fairness_metrics_set:
            query_params += "&fairnessMetricsSet={}".format(fairness_metrics_set)
        route = urljoin(self._get_model_url(), "fairnessInsights/{}".format(query_params))

        return self._client.get(route).json()

    def request_data_disparity_insights(self, feature, compared_class_names):
        """
        Request data disparity insights to be computed for the model.

        Parameters
        ----------
        feature : str
            Bias and Fairnes protected feature name.
        compared_class_names : list(str)
            List of two classes to compare

        Returns
        -------
        status_id : str
            A statusId of computation request.
        """
        route = "{}dataDisparityInsights/".format(self._get_model_url())
        response = self._client.post(
            route, data={"feature": feature, "compared_class_names": compared_class_names},
        )
        status_id = get_id_from_response(response)

        return status_id

    def get_data_disparity_insights(self, feature, class_name1, class_name2):
        """
        Retrieve a list of Cross Class Data Disparity insights for the model.

        Parameters
        ----------
        feature : str
            Bias and Fairnes protected feature name.
        class_name1 : str
            One of the compared classes
        class_name2 : str
            Another compared class

        Returns
        -------
        json
        """
        route = "{}dataDisparityInsights/?feature={}&className1={}&className2={}".format(
            self._get_model_url(), feature, class_name1, class_name2
        )
        return self._client.get(route).json()

    def request_cross_class_accuracy_scores(self):
        """
        Request data disparity insights to be computed for the model.

        Returns
        -------
        status_id : str
            A statusId of computation request.
        """
        route = "{}crossClassAccuracyScores/".format(self._get_model_url())
        response = self._client.post(route)
        status_id = get_id_from_response(response)

        return status_id

    def get_cross_class_accuracy_scores(self):
        """
        Retrieves a list of Cross Class Accuracy scores for the model.

        Returns
        -------
        json
        """
        route = "{}crossClassAccuracyScores/".format(self._get_model_url())

        return self._client.get(route).json()


class PrimeModel(Model):
    """Represents a DataRobot Prime model approximating a parent model with downloadable code.

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float
        the percentage of the project dataset used in training the model
    training_row_count : int or None
        the number of rows of the project dataset used in training the model.  In a datetime
        partitioned project, if specified, defines the number of rows used to train the model and
        evaluate backtest scores; if unspecified, either `training_duration` or
        `training_start_date` and `training_end_date` was used to determine that instead.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'DataRobot Prime'
    model_category : str
        what kind of model this is - always 'prime' for DataRobot Prime models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    ruleset : Ruleset
        the ruleset used in the Prime model
    parent_model_id : str
        the id of the model that this Prime model approximates
    monotonic_increasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically increasing relationship to the target.
        If None, no such constraints are enforced.
    monotonic_decreasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically decreasing relationship to the target.
        If None, no such constraints are enforced.
    supports_monotonic_constraints : bool
        optional, whether this model supports enforcing monotonic constraints
    is_starred : bool
        whether this model is marked as starred
    prediction_threshold : float
        for binary classification projects, the threshold used for predictions
    prediction_threshold_read_only : bool
        indicated whether modification of the prediction threshold is forbidden. Threshold
        modification is forbidden once a model has had a deployment created or predictions made via
        the dedicated prediction API.
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this model is supported in the Composable ML.
    """

    _converter = (
        t.Dict({t.Key("ruleset_id"): Int(), t.Key("rule_count"): Int(), t.Key("score"): t.Float()})
        + Model._converter
    ).allow_extra("*")

    def __init__(
        self,
        id=None,
        processes=None,
        featurelist_name=None,
        featurelist_id=None,
        project_id=None,
        sample_pct=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        model_type=None,
        model_category=None,
        is_frozen=None,
        blueprint_id=None,
        metrics=None,
        parent_model_id=None,
        ruleset_id=None,
        rule_count=None,
        score=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        supports_monotonic_constraints=None,
        is_starred=None,
        prediction_threshold=None,
        prediction_threshold_read_only=None,
        model_number=None,
        supports_composable_ml=None,
    ):
        super(PrimeModel, self).__init__(
            id=id,
            processes=processes,
            featurelist_name=featurelist_name,
            featurelist_id=featurelist_id,
            project_id=project_id,
            sample_pct=sample_pct,
            training_row_count=training_row_count,
            training_duration=training_duration,
            training_start_date=training_start_date,
            training_end_date=training_end_date,
            model_type=model_type,
            model_category=model_category,
            is_frozen=is_frozen,
            blueprint_id=blueprint_id,
            metrics=metrics,
            monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
            monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
            supports_monotonic_constraints=supports_monotonic_constraints,
            is_starred=is_starred,
            prediction_threshold=prediction_threshold,
            prediction_threshold_read_only=prediction_threshold_read_only,
            supports_composable_ml=supports_composable_ml,
        )
        ruleset_data = {
            "ruleset_id": ruleset_id,
            "rule_count": rule_count,
            "score": score,
            "model_id": id,
            "parent_model_id": parent_model_id,
            "project_id": project_id,
        }
        ruleset = Ruleset.from_data(ruleset_data)
        self.ruleset = ruleset
        self.parent_model_id = parent_model_id

    def __repr__(self):
        return "PrimeModel({!r})".format(self.model_type or self.id)

    def train(
        self,
        sample_pct=None,
        featurelist_id=None,
        scoring_type=None,
        training_row_count=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
    ):
        """
        Inherited from Model - PrimeModels cannot be retrained directly
        """
        raise NotImplementedError("PrimeModels cannot be retrained")

    @classmethod
    def get(cls, project_id, model_id):
        """
        Retrieve a specific prime model.

        Parameters
        ----------
        project_id : str
            The id of the project the prime model belongs to
        model_id : str
            The ``model_id`` of the prime model to retrieve.

        Returns
        -------
        model : PrimeModel
            The queried instance.
        """
        url = "projects/{}/primeModels/{}/".format(project_id, model_id)
        return cls.from_location(url)

    def request_download_validation(self, language):
        """Prep and validate the downloadable code for the ruleset associated with this model.

        Parameters
        ----------
        language : str
            the language the code should be downloaded in - see ``datarobot.enums.PRIME_LANGUAGE``
            for available languages

        Returns
        -------
        job : Job
            A job tracking the code preparation and validation
        """
        from . import Job

        data = {"model_id": self.id, "language": language}
        response = self._client.post("projects/{}/primeFiles/".format(self.project_id), data=data)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)


class BlenderModel(Model):
    """Represents blender model that combines prediction results from other models.

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float
        the percentage of the project dataset used in training the model
    training_row_count : int or None
        the number of rows of the project dataset used in training the model.  In a datetime
        partitioned project, if specified, defines the number of rows used to train the model and
        evaluate backtest scores; if unspecified, either `training_duration` or
        `training_start_date` and `training_end_date` was used to determine that instead.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'DataRobot Prime'
    model_category : str
        what kind of model this is - always 'prime' for DataRobot Prime models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    model_ids : list of str
        List of model ids used in blender
    blender_method : str
        Method used to blend results from underlying models
    monotonic_increasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically increasing relationship to the target.
        If None, no such constraints are enforced.
    monotonic_decreasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically decreasing relationship to the target.
        If None, no such constraints are enforced.
    supports_monotonic_constraints : bool
        optional, whether this model supports enforcing monotonic constraints
    is_starred : bool
        whether this model marked as starred
    prediction_threshold : float
        for binary classification projects, the threshold used for predictions
    prediction_threshold_read_only : bool
        indicated whether modification of the prediction threshold is forbidden. Threshold
        modification is forbidden once a model has had a deployment created or predictions made via
        the dedicated prediction API.
    model_number : integer
        model number assigned to a model
    parent_model_id : str or None
        (New in version v2.20) the id of the model that tuning parameters are derived from
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this model is supported in the Composable ML.
    """

    _converter = (
        t.Dict({t.Key("model_ids"): t.List(String), t.Key("blender_method"): String})
        + Model._converter
    ).allow_extra("*")

    def __init__(
        self,
        id=None,
        processes=None,
        featurelist_name=None,
        featurelist_id=None,
        project_id=None,
        sample_pct=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        model_type=None,
        model_category=None,
        is_frozen=None,
        blueprint_id=None,
        metrics=None,
        model_ids=None,
        blender_method=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        supports_monotonic_constraints=None,
        is_starred=None,
        prediction_threshold=None,
        prediction_threshold_read_only=None,
        model_number=None,
        parent_model_id=None,
        supports_composable_ml=None,
    ):
        super(BlenderModel, self).__init__(
            id=id,
            processes=processes,
            featurelist_name=featurelist_name,
            featurelist_id=featurelist_id,
            project_id=project_id,
            sample_pct=sample_pct,
            training_row_count=training_row_count,
            training_duration=training_duration,
            training_start_date=training_start_date,
            training_end_date=training_end_date,
            model_type=model_type,
            model_category=model_category,
            is_frozen=is_frozen,
            blueprint_id=blueprint_id,
            metrics=metrics,
            monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
            monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
            supports_monotonic_constraints=supports_monotonic_constraints,
            is_starred=is_starred,
            prediction_threshold=prediction_threshold,
            prediction_threshold_read_only=prediction_threshold_read_only,
            model_number=model_number,
            parent_model_id=parent_model_id,
            supports_composable_ml=supports_composable_ml,
        )
        self.model_ids = model_ids
        self.blender_method = blender_method

    @classmethod
    def get(cls, project_id, model_id):
        """Retrieve a specific blender.

        Parameters
        ----------
        project_id : str
            The project's id.
        model_id : str
            The ``model_id`` of the leaderboard item to retrieve.

        Returns
        -------
        model : BlenderModel
            The queried instance.
        """
        url = "projects/{}/blenderModels/{}/".format(project_id, model_id)
        return cls.from_location(url)

    def __repr__(self):
        return "BlenderModel({})".format(self.blender_method or self.id)


class FrozenModel(Model):
    """Represents a model tuned with parameters which are derived from another model

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float
        the percentage of the project dataset used in training the model
    training_row_count : int or None
        the number of rows of the project dataset used in training the model.  In a datetime
        partitioned project, if specified, defines the number of rows used to train the model and
        evaluate backtest scores; if unspecified, either `training_duration` or
        `training_start_date` and `training_end_date` was used to determine that instead.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    parent_model_id : str
        the id of the model that tuning parameters are derived from
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    monotonic_increasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically increasing relationship to the target.
        If None, no such constraints are enforced.
    monotonic_decreasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically decreasing relationship to the target.
        If None, no such constraints are enforced.
    supports_monotonic_constraints : bool
        optional, whether this model supports enforcing monotonic constraints
    is_starred : bool
        whether this model marked as starred
    prediction_threshold : float
        for binary classification projects, the threshold used for predictions
    prediction_threshold_read_only : bool
        indicated whether modification of the prediction threshold is forbidden. Threshold
        modification is forbidden once a model has had a deployment created or predictions made via
        the dedicated prediction API.
    model_number : integer
        model number assigned to a model
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this model is supported in the Composable ML.
    """

    _frozen_path_template = "projects/{}/frozenModels/"
    _converter = (Model._converter).allow_extra("*")

    def __init__(
        self,
        id=None,
        processes=None,
        featurelist_name=None,
        featurelist_id=None,
        project_id=None,
        sample_pct=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        model_type=None,
        model_category=None,
        is_frozen=None,
        blueprint_id=None,
        metrics=None,
        parent_model_id=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        supports_monotonic_constraints=None,
        is_starred=None,
        prediction_threshold=None,
        prediction_threshold_read_only=None,
        model_number=None,
        supports_composable_ml=None,
    ):
        super(FrozenModel, self).__init__(
            id=id,
            processes=processes,
            featurelist_name=featurelist_name,
            featurelist_id=featurelist_id,
            project_id=project_id,
            sample_pct=sample_pct,
            training_row_count=training_row_count,
            training_duration=training_duration,
            training_start_date=training_start_date,
            training_end_date=training_end_date,
            model_type=model_type,
            model_category=model_category,
            is_frozen=is_frozen,
            blueprint_id=blueprint_id,
            metrics=metrics,
            monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
            monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
            supports_monotonic_constraints=supports_monotonic_constraints,
            is_starred=is_starred,
            prediction_threshold=prediction_threshold,
            prediction_threshold_read_only=prediction_threshold_read_only,
            model_number=model_number,
            supports_composable_ml=supports_composable_ml,
        )
        self.parent_model_id = parent_model_id

    def __repr__(self):
        return "FrozenModel({!r})".format(self.model_type or self.id)

    @classmethod
    def get(cls, project_id, model_id):
        """
        Retrieve a specific frozen model.

        Parameters
        ----------
        project_id : str
            The project's id.
        model_id : str
            The ``model_id`` of the leaderboard item to retrieve.

        Returns
        -------
        model : FrozenModel
            The queried instance.
        """
        url = cls._frozen_path_template.format(project_id) + model_id + "/"
        return cls.from_location(url)


class DatetimeModel(Model):
    """Represents a model from a datetime partitioned project

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Note that only one of `training_row_count`, `training_duration`, and
    `training_start_date` and `training_end_date` will be specified, depending on the
    `data_selection_method` of the model.  Whichever method was selected determines the amount of
    data used to train on when making predictions and scoring the backtests and the holdout.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float
        the percentage of the project dataset used in training the model
    training_row_count : int or None
        If specified, an int specifying the number of rows used to train the model and evaluate
        backtest scores.
    training_duration : str or None
        If specified, a duration string specifying the duration spanned by the data used to train
        the model and evaluate backtest scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    time_window_sample_pct : int or None
        An integer between 1 and 99 indicating the percentage of sampling within the training
        window.  The points kept are determined by a random uniform sample.  If not specified, no
        sampling was done.
    sampling_method : str or None
        (New in v2.23) indicates the way training data has been selected (either how rows have been
        selected within backtest or how ``time_window_sample_pct`` has been applied).
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric.  The keys in metrics are
        the different metrics used to evaluate the model, and the values are the results.  The
        dictionaries inside of metrics will be as described here: 'validation', the score
        for a single backtest; 'crossValidation', always None; 'backtesting', the average score for
        all backtests if all are available and computed, or None otherwise; 'backtestingScores', a
        list of scores for all backtests where the score is None if that backtest does not have a
        score available; and 'holdout', the score for the holdout or None if the holdout is locked
        or the score is unavailable.
    backtests : list of dict
        describes what data was used to fit each backtest, the score for the project metric, and
        why the backtest score is unavailable if it is not provided.
    data_selection_method : str
        which of training_row_count, training_duration, or training_start_data and training_end_date
        were used to determine the data used to fit the model.  One of 'rowCount',
        'duration', or 'selectedDateRange'.
    training_info : dict
        describes which data was used to train on when scoring the holdout and making predictions.
        training_info` will have the following keys: `holdout_training_start_date`,
        `holdout_training_duration`, `holdout_training_row_count`, `holdout_training_end_date`,
        `prediction_training_start_date`, `prediction_training_duration`,
        `prediction_training_row_count`, `prediction_training_end_date`. Start and end dates will
        be datetimes, durations will be duration strings, and rows will be integers.
    holdout_score : float or None
        the score against the holdout, if available and the holdout is unlocked, according to the
        project metric.
    holdout_status : string or None
        the status of the holdout score, e.g. "COMPLETED", "HOLDOUT_BOUNDARIES_EXCEEDED".
        Unavailable if the holdout fold was disabled in the partitioning configuration.
    monotonic_increasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically increasing relationship to the target.
        If None, no such constraints are enforced.
    monotonic_decreasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically decreasing relationship to the target.
        If None, no such constraints are enforced.
    supports_monotonic_constraints : bool
        optional, whether this model supports enforcing monotonic constraints
    is_starred : bool
        whether this model marked as starred
    prediction_threshold : float
        for binary classification projects, the threshold used for predictions
    prediction_threshold_read_only : bool
        indicated whether modification of the prediction threshold is forbidden. Threshold
        modification is forbidden once a model has had a deployment created or predictions made via
        the dedicated prediction API.
    effective_feature_derivation_window_start : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the past relative to the forecast point
        the user needs to provide history for at prediction time. This can differ from the
        ``feature_derivation_window_start`` set on the project due to the differencing method and
        period selected, or if the model is a time series native model such as ARIMA. Will be a
        negative integer in time series projects and ``None`` otherwise.
    effective_feature_derivation_window_end : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the past relative to the forecast point
        the feature derivation window should end. Will be a non-positive integer in time series
        projects and ``None`` otherwise.
    forecast_window_start : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the future relative to the forecast point
        the forecast window should start. Note that this field will be the same as what is shown in
        the project settings. Will be a non-negative integer in time series projects and `None`
        otherwise.
    forecast_window_end : int or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        How many units of the ``windows_basis_unit`` into the future relative to the forecast point
        the forecast window should end. Note that this field will be the same as what is shown in
        the project settings. Will be a non-negative integer in time series projects and `None`
        otherwise.
    windows_basis_unit : str or None
        (New in v2.16) For :ref:`time series <time_series>` projects only.
        Indicates which unit is the basis for the feature derivation window and the forecast window.
        Note that this field will be the same as what is shown in the project settings. In time
        series projects, will be either the detected time unit or "ROW", and `None` otherwise.
    model_number : integer
        model number assigned to a model
    parent_model_id : str or None
        (New in version v2.20) the id of the model that tuning parameters are derived from
    use_project_settings : bool or None
        (New in version v2.20) If ``True``, indicates that the custom backtest partitioning settings
        specified by the user were used to train the model and evaluate backtest scores.
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this model is supported in the Composable ML.
    """

    _training_info_converter = t.Dict(
        {
            t.Key("holdout_training_start_date", default=None): parse_time,
            t.Key("holdout_training_duration", default=None): t.Or(String(), t.Null),
            t.Key("holdout_training_row_count", default=None): t.Or(Int(), t.Null()),
            t.Key("holdout_training_end_date", default=None): parse_time,
            t.Key("prediction_training_start_date"): parse_time,
            t.Key("prediction_training_duration"): String(),
            t.Key("prediction_training_row_count"): Int(),
            t.Key("prediction_training_end_date"): parse_time,
        }
    ).ignore_extra("*")
    _backtest_converter = t.Dict(
        {
            t.Key("index"): Int(),
            t.Key("score", default=None): t.Or(t.Float(), t.Null),
            t.Key("status"): String(),
            t.Key("training_start_date", default=None): parse_time,
            t.Key("training_duration", default=None): t.Or(String(), t.Null),
            t.Key("training_row_count", default=None): t.Or(Int(), t.Null()),
            t.Key("training_end_date", default=None): parse_time,
        }
    ).ignore_extra("*")
    _converter = (
        t.Dict(
            {
                t.Key("training_info"): _training_info_converter,
                t.Key("time_window_sample_pct", optional=True): Int(),
                t.Key("sampling_method", optional=True): t.Or(String(), t.Null()),
                t.Key("holdout_score", optional=True): t.Float(),
                t.Key("holdout_status", optional=True): String(),
                t.Key("data_selection_method"): String(),
                t.Key("backtests"): t.List(_backtest_converter),
                t.Key("effective_feature_derivation_window_start", optional=True): Int(lte=0),
                t.Key("effective_feature_derivation_window_end", optional=True): Int(lte=0),
                t.Key("forecast_window_start", optional=True): Int(gte=0),
                t.Key("forecast_window_end", optional=True): Int(gte=0),
                t.Key("windows_basis_unit", optional=True): String(),
            }
        )
        + Model._converter
    ).ignore_extra("*")

    _base_datetime_model_path_template = "projects/{}/datetimeModels/"

    def __init__(
        self,
        id=None,
        processes=None,
        featurelist_name=None,
        featurelist_id=None,
        project_id=None,
        sample_pct=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        time_window_sample_pct=None,
        sampling_method=None,
        model_type=None,
        model_category=None,
        is_frozen=None,
        blueprint_id=None,
        metrics=None,
        training_info=None,
        holdout_score=None,
        holdout_status=None,
        data_selection_method=None,
        backtests=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        supports_monotonic_constraints=None,
        is_starred=None,
        prediction_threshold=None,
        prediction_threshold_read_only=None,
        effective_feature_derivation_window_start=None,
        effective_feature_derivation_window_end=None,
        forecast_window_start=None,
        forecast_window_end=None,
        windows_basis_unit=None,
        model_number=None,
        parent_model_id=None,
        use_project_settings=None,
        supports_composable_ml=None,
    ):
        super(DatetimeModel, self).__init__(
            id=id,
            processes=processes,
            featurelist_name=featurelist_name,
            featurelist_id=featurelist_id,
            project_id=project_id,
            sample_pct=sample_pct,
            training_row_count=training_row_count,
            training_duration=training_duration,
            training_start_date=training_start_date,
            training_end_date=training_end_date,
            model_type=model_type,
            model_category=model_category,
            is_frozen=is_frozen,
            blueprint_id=blueprint_id,
            metrics=metrics,
            monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
            monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
            supports_monotonic_constraints=supports_monotonic_constraints,
            is_starred=is_starred,
            prediction_threshold=prediction_threshold,
            prediction_threshold_read_only=prediction_threshold_read_only,
            model_number=model_number,
            parent_model_id=parent_model_id,
            use_project_settings=use_project_settings,
            supports_composable_ml=supports_composable_ml,
        )
        self.time_window_sample_pct = time_window_sample_pct
        self.sampling_method = sampling_method
        self.training_info = training_info
        self.holdout_score = holdout_score
        self.holdout_status = holdout_status
        self.data_selection_method = data_selection_method
        self.backtests = backtests
        self.effective_feature_derivation_window_start = effective_feature_derivation_window_start
        self.effective_feature_derivation_window_end = effective_feature_derivation_window_end
        self.forecast_window_start = forecast_window_start
        self.forecast_window_end = forecast_window_end
        self.windows_basis_unit = windows_basis_unit
        # Private attributes
        self._base_datetime_model_path = self._base_datetime_model_path_template.format(
            self.project_id
        )

    def __repr__(self):
        return "DatetimeModel({!r})".format(self.model_type or self.id)

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        """Instantiate a DatetimeModel with data from the server, modifying casing as needed.

        Overrides the inherited method since the model must _not_ recursively change casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        keep_attrs: list
            Allow these attributes to stay even if they have None value
        """

        def cut_attr_level(pattern):
            if keep_attrs:
                return [
                    attr.replace(pattern, "", 1) for attr in keep_attrs if attr.startswith(pattern)
                ]
            else:
                return None

        case_converted = from_api(data, do_recursive=False, keep_attrs=keep_attrs)
        case_converted["training_info"] = from_api(
            case_converted["training_info"], keep_attrs=cut_attr_level("training_info.")
        )
        case_converted["backtests"] = from_api(
            case_converted["backtests"], keep_attrs=cut_attr_level("backtests.")
        )
        return cls.from_data(case_converted)

    @classmethod
    def get(cls, project, model_id):
        """Retrieve a specific datetime model.

        If the project does not use datetime partitioning, a ClientError will occur.

        Parameters
        ----------
        project : str
            the id of the project the model belongs to
        model_id : str
            the id of the model to retrieve

        Returns
        -------
        model : DatetimeModel
            the model
        """
        url = "projects/{}/datetimeModels/{}/".format(project, model_id)
        return cls.from_location(url)

    def train(
        self,
        sample_pct=None,
        featurelist_id=None,
        scoring_type=None,
        training_row_count=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
    ):
        """Inherited from Model - DatetimeModels cannot be retrained with this method

        Use train_datetime instead.
        """
        msg = "DatetimeModels cannot be retrained by sample percent, use train_datetime instead"
        raise NotImplementedError(msg)

    def request_frozen_model(self, sample_pct=None, training_row_count=None):
        """Inherited from Model - DatetimeModels cannot be retrained with this method

        Use request_frozen_datetime_model instead.
        """
        msg = (
            "DatetimeModels cannot train frozen models by sample percent, "
            "use request_frozen_datetime_model instead"
        )
        raise NotImplementedError(msg)

    def score_backtests(self):
        """Compute the scores for all available backtests.

        Some backtests may be unavailable if the model is trained into their validation data.

        Returns
        -------
        job : Job
            a job tracking the backtest computation.  When it is complete, all available backtests
            will have scores computed.
        """
        from .job import Job

        url = "projects/{}/datetimeModels/{}/backtests/".format(self.project_id, self.id)
        res = self._client.post(url)
        return Job.get(self.project_id, get_id_from_response(res))

    def cross_validate(self):
        """Inherited from the model. DatetimeModels cannot request cross validation scores;
        use backtests instead.
        """
        msg = "DatetimeModels cannot request cross validation, use score_backtests instead"
        raise NotImplementedError(msg)

    def get_cross_validation_scores(self, partition=None, metric=None):
        """Inherited from Model - DatetimeModels cannot request Cross Validation scores,

        Use ``backtests`` instead.
        """
        msg = (
            "DatetimeModels cannot request cross validation scores, "
            "see backtests attribute instead"
        )
        raise NotImplementedError(msg)

    def request_training_predictions(self, data_subset):
        """Start a job that builds training predictions.

        Parameters
        ----------
        data_subset : str
            data set definition to build predictions on.
            Choices are:

                - `dr.enums.DATA_SUBSET.HOLDOUT` for holdout data set only
                - `dr.enums.DATA_SUBSET.ALL_BACKTESTS` for downloading the predictions for all
                   backtest validation folds. Requires the model to have successfully scored all
                   backtests.
        Returns
        -------
        Job
            an instance of created async job
        """

        return super(DatetimeModel, self).request_training_predictions(data_subset=data_subset)

    def get_series_accuracy_as_dataframe(
        self,
        offset=0,
        limit=100,
        metric=None,
        multiseries_value=None,
        order_by=None,
        reverse=False,
    ):
        """Retrieve series accuracy results for the specified model as a pandas.DataFrame.

        Parameters
        ----------
        offset : int, optional
            The number of results to skip. Defaults to 0 if not specified.
        limit : int, optional
            The maximum number of results to return. Defaults to 100 if not specified.
        metric : str, optional
            The name of the metric to retrieve scores for. If omitted, the default project metric
            will be used.
        multiseries_value : str, optional
            If specified, only the series containing the given value in one of the series ID columns
            will be returned.
        order_by : str, optional
            Used for sorting the series. Attribute must be one of
            ``datarobot.enums.SERIES_ACCURACY_ORDER_BY``.
        reverse : bool, optional
            Used for sorting the series. If ``True``, will sort the series in descending order by
            the attribute specified by ``order_by``.

        Returns
        -------
        data
            A pandas.DataFrame with the Series Accuracy for the specified model.

        """

        initial_params = {
            "offset": offset,
            "limit": limit,
        }
        if metric:
            initial_params["metric"] = metric
        if multiseries_value:
            initial_params["multiseriesValue"] = multiseries_value
        if order_by:
            initial_params["orderBy"] = "-" + order_by if reverse else order_by

        url = "projects/{}/datetimeModels/{}/multiseriesScores/".format(self.project_id, self.id)
        return pd.DataFrame(unpaginate(url, initial_params, self._client))

    def download_series_accuracy_as_csv(
        self,
        filename,
        encoding="utf-8",
        offset=0,
        limit=100,
        metric=None,
        multiseries_value=None,
        order_by=None,
        reverse=False,
    ):
        """Save series accuracy results for the specified model in a CSV file.

        Parameters
        ----------
        filename : str or file object
            The path or file object to save the data to.
        encoding : str, optional
            A string representing the encoding to use in the output csv file.
            Defaults to 'utf-8'.
        offset : int, optional
            The number of results to skip. Defaults to 0 if not specified.
        limit : int, optional
            The maximum number of results to return. Defaults to 100 if not specified.
        metric : str, optional
            The name of the metric to retrieve scores for. If omitted, the default project metric
            will be used.
        multiseries_value : str, optional
            If specified, only the series containing the given value in one of the series ID columns
            will be returned.
        order_by : str, optional
            Used for sorting the series. Attribute must be one of
            ``datarobot.enums.SERIES_ACCURACY_ORDER_BY``.
        reverse : bool, optional
            Used for sorting the series. If ``True``, will sort the series in descending order by
            the attribute specified by ``order_by``.
        """

        data = self.get_series_accuracy_as_dataframe(
            offset=offset,
            limit=limit,
            metric=metric,
            multiseries_value=multiseries_value,
            order_by=order_by,
            reverse=reverse,
        )
        data.to_csv(
            path_or_buf=filename, header=True, index=False, encoding=encoding,
        )

    def compute_series_accuracy(self, compute_all_series=False):
        """Compute series accuracy for the model.

        Parameters
        ----------
        compute_all_series : bool, optional
            Calculate accuracy for all series or only first 1000.

        Returns
        -------
        Job
            an instance of the created async job
        """
        data = {"compute_all_series": True} if compute_all_series else {}
        url = "projects/{}/datetimeModels/{}/multiseriesScores/".format(self.project_id, self.id)
        compute_response = self._client.post(url, data)
        from .job import Job

        return Job.get(self.project_id, get_id_from_response(compute_response))

    def retrain(
        self,
        time_window_sample_pct=None,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        sampling_method=None,
    ):
        """Retrain an existing datetime model using a new training period for the model's training
        set (with optional time window sampling) or a different feature list.

        All durations should be specified with a duration string such as those returned
        by the :meth:`partitioning_methods.construct_duration_string
        <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
        Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
        for more information on duration strings.

        Parameters
        ----------
        featurelist_id : str, optional
            The ID of the featurelist to use.
        training_row_count : str, optional
            The number of rows to train the model on. If this parameter is used then `sample_pct`
            cannot be specified.
        time_window_sample_pct : int, optional
            An int between ``1`` and ``99`` indicating the percentage of
            sampling within the time window. The points kept are determined by a random uniform
            sample. If specified, `training_row_count` must not be specified and either
            `training_duration` or `training_start_date` and `training_end_date` must be specified.
        training_duration : str, optional
            A duration string representing the training duration for the submitted model. If
            specified then `training_row_count`, `training_start_date`, and `training_end_date`
            cannot be specified.
        training_start_date : str, optional
            A datetime string representing the start date of
            the data to use for training this model.  If specified, `training_end_date` must also be
            specified, and `training_duration` cannot be specified. The value must be before the
            `training_end_date` value.
        training_end_date : str, optional
            A datetime string representing the end date of the
            data to use for training this model.  If specified, `training_start_date` must also be
            specified, and `training_duration` cannot be specified. The value must be after the
            `training_start_date` value.
        sampling_method : str, optional
            (New in version v2.23) defines the way training data is selected. Can be either
            ``random`` or ``latest``.  In combination with ``training_row_count`` defines how rows
            are selected from backtest (``latest`` by default).  When training data is defined using
            time range (``training_duration`` or ``use_project_settings``) this setting changes the
            way ``time_window_sample_pct`` is applied (``random`` by default).  Applicable to OTV
            projects only.

        Returns
        -------
        job : ModelJob
            The created job that is retraining the model
        """
        if bool(training_start_date) ^ bool(training_end_date):
            raise ValueError("Both training_start_date and training_end_date must be specified.")
        if training_duration and training_row_count:
            raise ValueError(
                "Only one of training_duration or training_row_count should be specified."
            )
        if time_window_sample_pct and not training_duration and not training_start_date:
            raise ValueError(
                "time_window_sample_pct should only be used with either "
                "training_duration or training_start_date and training_end_date"
            )
        from .modeljob import ModelJob

        url = "projects/{}/datetimeModels/fromModel/".format(self.project_id)
        payload = {
            "modelId": self.id,
            "featurelistId": featurelist_id,
            "timeWindowSamplePct": time_window_sample_pct,
            "trainingRowCount": training_row_count,
            "trainingDuration": training_duration,
            "trainingStartDate": training_start_date,
            "trainingEndDate": training_end_date,
        }
        if sampling_method:
            payload["samplingMethod"] = sampling_method
        response = self._client.post(url, data=payload)
        return ModelJob.from_id(self.project_id, get_id_from_response(response))

    def _get_datetime_model_url(self):
        if self.id is None:
            # This check is why this is a method instead of an attribute. Once we stop creating
            # models without model id's in the tests, we can make this an attribute we set in the
            # constructor.
            raise ValueError("Sorry, id attribute is None so I can't make the url to this model.")
        return "{}{}/".format(self._base_datetime_model_path, self.id)

    def _get_feature_effect_metadata_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_datetime_model_url() + "featureEffectsMetadata/"

    def get_feature_effect_metadata(self):
        """
        Retrieve Feature Effect metadata for each backtest. Response contains status and available
        sources for each backtest of the model.

        * Each backtest is available for `training` and `validation`

        * If holdout is configured for the project it has `holdout` as `backtestIndex`. It has
          `training` and `holdout` sources available.

        Start/stop models contain a single response item with `startstop` value for `backtestIndex`.

        * Feature Effect of `training` is always available
          (except for the old project which supports only Feature Effect for `validation`).

        * When a model is trained into `validation` or `holdout` without stacked prediction
          (e.g. no out-of-sample prediction in `validation` or `holdout`),
          Feature Effect is not available for `validation` or `holdout`.

        * Feature Effect for `holdout` is not available when there is no holdout configured for
          the project.

        `source` is expected parameter to retrieve Feature Effect. One of provided sources
        shall be used.

        `backtestIndex` is expected parameter to submit compute request and retrieve Feature Effect.
        One of provided backtest indexes shall be used.

        Returns
        -------
        feature_effect_metadata: FeatureEffectMetadataDatetime

        """
        fe_metadata_url = self._get_feature_effect_metadata_url()
        server_data = self._client.get(fe_metadata_url).json()
        return FeatureEffectMetadataDatetime.from_server_data(server_data)

    def _get_feature_fit_metadata_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_datetime_model_url() + "featureFitMetadata/"

    def get_feature_fit_metadata(self):
        """
        Retrieve Feature Fit metadata for each backtest. Response contains status and available
        sources for each backtest of the model.

        * Each backtest is available for `training` and `validation`

        * If holdout is configured for the project it has `holdout` as `backtestIndex`. It has
          `training` and `holdout` sources available.

        Start/stop models contain a single response item with `startstop` value for `backtestIndex`.

        * Feature Fit of `training` is always available
          (except for the old project which supports only Feature Effect for `validation`).

        * When a model is trained into `validation` or `holdout` without stacked prediction
          (e.g. no out-of-sample prediction in `validation` or `holdout`),
          Feature Fit is not available for `validation` or `holdout`.

        * Feature Fit for `holdout` is not available when there is no holdout configured for
          the project.

        `source` is expected parameter to retrieve Feature Fit. One of provided sources
        shall be used.

        `backtestIndex` is expected parameter to submit compute request and retrieve Feature Fit.
        One of provided backtest indexes shall be used.

        Returns
        -------
        feature_effect_metadata: FeatureFitMetadataDatetime

        """
        ff_metadata_url = self._get_feature_fit_metadata_url()
        server_data = self._client.get(ff_metadata_url).json()
        return FeatureFitMetadataDatetime.from_server_data(server_data)

    def _get_feature_effect_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_datetime_model_url() + "featureEffects/"

    def request_feature_effect(self, backtest_index):
        """
        Request feature effects to be computed for the model.

        See :meth:`get_feature_effect <datarobot.models.DatetimeModel.get_feature_effect>` for more
        information on the result of the job.

        See :meth:`get_feature_effect_metadata \
        <datarobot.models.DatetimeModel.get_feature_effect_metadata>`
        for retrieving information of backtest_index.

        Parameters
        ----------
        backtest_index: string, FeatureEffectMetadataDatetime.backtest_index.
            The backtest index to retrieve Feature Effects for.

        Returns
        -------
         job : Job
            A Job representing the feature effect computation. To get the completed feature effect
            data, use `job.get_result` or `job.get_result_when_complete`.

        Raises
        ------
        JobAlreadyRequested (422)
            If the feature effect have already been requested.
        """
        from .job import Job

        payload = {"backtestIndex": backtest_index}
        route = self._get_feature_effect_url()
        response = self._client.post(route, data=payload)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def get_feature_effect(self, source, backtest_index, include_ice_plots=False):
        """
        Retrieve Feature Effects for the model.

        Feature Effects provides partial dependence and predicted vs actual values for top-500
        features ordered by feature impact score.

        The partial dependence shows marginal effect of a feature on the target variable after
        accounting for the average effects of all other predictive features. It indicates how,
        holding all other variables except the feature of interest as they were,
        the value of this feature affects your prediction.

        Requires that Feature Effects has already been computed with
        :meth:`request_feature_effect <datarobot.models.Model.request_feature_effect>`.

        See :meth:`get_feature_effect_metadata \
        <datarobot.models.DatetimeModel.get_feature_effect_metadata>`
        for retrieving information of source, backtest_index.

        Parameters
        ----------
        source: string
            The source Feature Effects are retrieved for.
            One value of [FeatureEffectMetadataDatetime.sources]. To retrieve the availiable
            sources for feature effect.

        backtest_index: string, FeatureEffectMetadataDatetime.backtest_index.
            The backtest index to retrieve Feature Effects for.

        include_ice_plots: bool, optional
            Indicates whether Individual Conditional Expectation (ICE) plots should be returned.

        Returns
        -------
        feature_effects: FeatureEffects
           The feature effects data.

        Raises
        ------
        ClientError (404)
            If the feature effects have not been computed or source is not valid value.
        """
        params = {
            "source": source,
            "backtestIndex": backtest_index,
            "includeIcePlots": include_ice_plots,
        }
        fe_url = self._get_feature_effect_url()
        server_data = self._client.get(fe_url, params=params).json()
        return FeatureEffects.from_server_data(server_data)

    def get_or_request_feature_effect(self, source, backtest_index, max_wait=DEFAULT_MAX_WAIT):
        """
        Retrieve feature effect for the model, requesting a job if it hasn't been run previously

        See :meth:`get_feature_effect_metadata \
        <datarobot.models.DatetimeModel.get_feature_effect_metadata>`
        for retrieving information of source, backtest_index.

        Parameters
        ----------
        max_wait : int, optional
            The maximum time to wait for a requested feature effect job to complete before erroring

        source : string
            The source Feature Effects are retrieved for.
            One value of [FeatureEffectMetadataDatetime.sources]. To retrieve the availiable sources
            for feature effect.

        backtest_index: string, FeatureEffectMetadataDatetime.backtest_index.
            The backtest index to retrieve Feature Effects for.

        Returns
        -------
        feature_effects : FeatureEffects
           The feature effects data.
        """
        try:
            feature_effect_job = self.request_feature_effect(backtest_index)
        except JobAlreadyRequested as e:
            # if already requested it may be still running
            # check and get the jobid in that case
            qid = e.json["jobId"]
            from .job import Job

            feature_effect_job = Job.get(self.project_id, qid)

        params = {"source": source}
        return feature_effect_job.get_result_when_complete(max_wait=max_wait, params=params)

    def request_feature_effects_multiclass(
        self, backtest_index, row_count=None, top_n_features=None, features=None,
    ):
        """
        Request feature effects to be computed for the multiclass datetime model.

        See :meth:`get_feature_effect <datarobot.models.Model.get_feature_effects_multiclass>` for
        more information on the result of the job.

        Parameters
        ----------
        backtest_index : str
            The backtest index to use for Feature Effects calculation.
        row_count : int
            The number of rows from dataset to use for Feature Impact calculation.
        top_n_features : int or None
            Number of top features (ranked by Feature Impact) used to calculate Feature Effects.
        features : list or None
            The list of features to use to calculate Feature Effects.

        Returns
        -------
         job : Job
            A Job representing Feature Effects computation. To get the completed Feature Effect
            data, use `job.get_result` or `job.get_result_when_complete`.
        """
        return FeatureEffectsMulticlass.create(
            project_id=self.project_id,
            model_id=self.id,
            backtest_index=backtest_index,
            row_count=row_count,
            top_n_features=top_n_features,
            features=features,
        )

    def get_feature_effects_multiclass(self, backtest_index, source="training", class_=None):
        """
        Retrieve Feature Effects for the multiclass datetime model.

        Feature Effects provides partial dependence and predicted vs actual values for top-500
        features ordered by feature impact score.

        The partial dependence shows marginal effect of a feature on the target variable after
        accounting for the average effects of all other predictive features. It indicates how,
        holding all other variables except the feature of interest as they were,
        the value of this feature affects your prediction.

        Requires that Feature Effects has already been computed with
        :meth:`request_feature_effect <datarobot.models.Model.request_feature_effect>`.

        See :meth:`get_feature_effect_metadata <datarobot.models.Model.get_feature_effect_metadata>`
        for retrieving information the availiable sources.

        Parameters
        ----------
        backtest_index : str
            The backtest index to retrieve Feature Effects for.
        source : str
            The source Feature Effects are retrieved for.
        class_ : str or None
            The class name Feature Effects are retrieved for.

        Returns
        -------
        list
           The list of multiclass Feature Effects.

        Raises
        ------
        ClientError (404)
            If the Feature Effects have not been computed or source is not valid value.
        """
        return FeatureEffectsMulticlass.get(
            project_id=self.project_id,
            model_id=self.id,
            backtest_index=backtest_index,
            source=source,
            class_=class_,
        )

    def get_or_request_feature_effects_multiclass(
        self,
        backtest_index,
        source,
        top_n_features=None,
        features=None,
        row_count=None,
        class_=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Feature Effects for a datetime multiclass model, and request a job if it hasn't
        been run previously.

        Parameters
        ----------
        backtest_index : str
            The backtest index to retrieve Feature Effects for.
        source : string
            The source from which Feature Effects are retrieved.
        class_ : str or None
            The class name Feature Effects retrieve for.
        row_count : int
            The number of rows used from the dataset for Feature Impact calculation.
        top_n_features : int or None
            Number of top features (ranked by feature impact) used to calculate Feature Effects.
        features : list or None
            The list of features used to calculate Feature Effects.
        max_wait : int, optional
            The maximum time to wait for a requested feature effect job to complete before erroring.

        Returns
        -------
        feature_effects : list of FeatureEffectsMulticlass
           The list of multiclass feature effects data.
        """
        try:
            feature_effects = self.get_feature_effects_multiclass(
                backtest_index=backtest_index, source=source, class_=class_
            )
        except ClientError as e:
            if e.status_code == 404 and "No data found for model" in e.json.get("message"):
                feature_effects_job = self.request_feature_effects_multiclass(
                    backtest_index=backtest_index,
                    row_count=row_count,
                    top_n_features=top_n_features,
                    features=features,
                )
                params = {"source": source}
                if class_:
                    params["class"] = class_
                feature_effects = feature_effects_job.get_result_when_complete(
                    max_wait=max_wait, params=params
                )
            else:
                raise e

        return feature_effects

    def _get_feature_fit_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_datetime_model_url() + "featureFit/"

    def request_feature_fit(self, backtest_index):
        """
        Request feature fit to be computed for the model.

        See :meth:`get_feature_fit <datarobot.models.DatetimeModel.get_feature_fit>` for more
        information on the result of the job.

        See :meth:`get_feature_fit_metadata \
        <datarobot.models.DatetimeModel.get_feature_fit_metadata>`
        for retrieving information of backtest_index.

        Parameters
        ----------
        backtest_index: string, FeatureFitMetadataDatetime.backtest_index.
            The backtest index to retrieve Feature Fit for.

        Returns
        -------
         job : Job
            A Job representing the feature fit computation. To get the completed feature fit
            data, use `job.get_result` or `job.get_result_when_complete`.

        Raises
        ------
        JobAlreadyRequested (422)
            If the feature fit have already been requested.
        """
        from .job import Job

        payload = {"backtestIndex": backtest_index}
        route = self._get_feature_fit_url()
        response = self._client.post(route, data=payload)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def get_feature_fit(self, source, backtest_index, include_ice_plots=False):
        """
        Retrieve Feature Fit for the model.

        Feature Fit provides partial dependence and predicted vs actual values for top-500
        features ordered by feature impact score.

        The partial dependence shows marginal effect of a feature on the target variable after
        accounting for the average effects of all other predictive features. It indicates how,
        holding all other variables except the feature of interest as they were,
        the value of this feature affects your prediction.

        Requires that Feature Fit has already been computed with
        :meth:`request_feature_fit <datarobot.models.Model.request_feature_fit>`.

        See :meth:`get_feature_fit_metadata \
        <datarobot.models.DatetimeModel.get_feature_fit_metadata>`
        for retrieving information of source, backtest_index.

        Parameters
        ----------
        source: string
            The source Feature Fit are retrieved for.
            One value of [FeatureFitMetadataDatetime.sources]. To retrieve the availiable
            sources for feature fit.

        backtest_index: string, FeatureFitMetadataDatetime.backtest_index.
            The backtest index to retrieve Feature Fit for.

        include_ice_plots: bool, optional
            Indicates whether Individual Conditional Expectation (ICE) plots should be returned.

        Returns
        -------
        feature_fit: FeatureFit
           The feature fit data.

        Raises
        ------
        ClientError (404)
            If the feature fit have not been computed or source is not valid value.
        """
        params = {
            "source": source,
            "backtestIndex": backtest_index,
            "includeIcePlots": include_ice_plots,
        }
        fe_url = self._get_feature_fit_url()
        server_data = self._client.get(fe_url, params=params).json()
        return FeatureFit.from_server_data(server_data)

    def get_or_request_feature_fit(self, source, backtest_index, max_wait=DEFAULT_MAX_WAIT):
        """
        Retrieve feature fit for the model, requesting a job if it hasn't been run previously

        See :meth:`get_feature_fit_metadata \
        <datarobot.models.DatetimeModel.get_feature_fit_metadata>`
        for retrieving information of source, backtest_index.

        Parameters
        ----------
        max_wait : int, optional
            The maximum time to wait for a requested feature fit job to complete before erroring

        source : string
            The source Feature Fit are retrieved for.
            One value of [FeatureFitMetadataDatetime.sources]. To retrieve the availiable sources
            for feature effect.

        backtest_index: string, FeatureFitMetadataDatetime.backtest_index.
            The backtest index to retrieve Feature Fit for.

        Returns
        -------
        feature_fit : FeatureFit
           The feature fit data.
        """
        try:
            feature_fit_job = self.request_feature_fit(backtest_index)
        except JobAlreadyRequested as e:
            # if already requested it may be still running
            # check and get the jobid in that case
            qid = e.json["jobId"]
            from .job import Job

            feature_fit_job = Job.get(self.project_id, qid)

        params = {"source": source}
        return feature_fit_job.get_result_when_complete(max_wait=max_wait, params=params)

    def calculate_prediction_intervals(self, prediction_intervals_size):
        """
        Calculate prediction intervals for this DatetimeModel for the specified size.

        .. versionadded:: v2.19

        Parameters
        ----------
        prediction_intervals_size : int
            The prediction intervals size to calculate for this model. See the
            :ref:`prediction intervals <prediction_intervals>` documentation for more information.

        Returns
        -------
        job : Job
            a :py:class:`Job <datarobot.models.Job>` tracking the prediction intervals computation
        """
        url = "projects/{}/models/{}/predictionIntervals/".format(self.project_id, self.id)
        payload = {"percentiles": [prediction_intervals_size]}
        res = self._client.post(url, data=payload)
        from .job import Job

        return Job.get(self.project_id, get_id_from_response(res))

    def get_calculated_prediction_intervals(self, offset=None, limit=None):
        """
        Retrieve a list of already-calculated prediction intervals for this model

        .. versionadded:: v2.19

        Parameters
        ----------
        offset : int, optional
            If provided, this many results will be skipped
        limit : int, optional
            If provided, at most this many results will be returned. If not provided, will return
            at most 100 results.

        Returns
        -------
        list[int]
            A descending-ordered list of already-calculated prediction interval sizes
        """
        url = "projects/{}/models/{}/predictionIntervals/".format(self.project_id, self.id)
        params = {}
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        return [interval for interval in unpaginate(url, params, self._client)]

    def compute_datetime_trend_plots(
        self,
        backtest=0,
        source=SOURCE_TYPE.VALIDATION,
        forecast_distance_start=None,
        forecast_distance_end=None,
    ):
        """
        Computes datetime trend plots
        (Accuracy over Time, Forecast vs Actual, Anomaly over Time) for this model

        .. versionadded:: v2.25

        Parameters
        ----------
        backtest : int or string, optional
            Compute plots for a specific backtest (use the backtest index starting from zero).
            To compute plots for holdout, use ``dr.enums.DATA_SUBSET.HOLDOUT``
        source : string, optional
            The source of the data for the backtest/holdout.
            Attribute must be one of ``dr.enums.SOURCE_TYPE``
        forecast_distance_start : int, optional:
            The start of forecast distance range (forecast window) to compute.
            If not specified, the first forecast distance for this project will be used.
            Only for time series supervised models
        forecast_distance_end : int, optional:
            The end of forecast distance range (forecast window) to compute.
            If not specified, the last forecast distance for this project will be used.
            Only for time series supervised models

        Returns
        -------
        job : Job
            a :py:class:`Job <datarobot.models.Job>` tracking the datetime trend plots computation

        Notes
        -----
            * Forecast distance specifies the number of time steps
              between the predicted point and the origin point.
            * For the multiseries models only first 1000 series in
              alphabetical order and an average plot for them will be computed.
            * Maximum 100 forecast distances can be requested for
              calculation in time series supervised projects.
        """
        url = "projects/{project_id}/datetimeModels/{model_id}/datetimeTrendPlots/".format(
            project_id=self.project_id, model_id=self.id
        )
        payload = {
            "backtest": backtest,
            "source": source,
            "forecastDistanceStart": forecast_distance_start,
            "forecastDistanceEnd": forecast_distance_end,
        }
        result = self._client.post(url, data=payload)
        from .job import Job

        return Job.get(self.project_id, get_id_from_response(result))

    def get_accuracy_over_time_plots_metadata(self, forecast_distance=None):
        """
        Retrieve Accuracy over Time plots metadata for this model.

        .. versionadded:: v2.25

        Parameters
        ----------
        forecast_distance : int, optional
            Forecast distance to retrieve the metadata for.
            If not specified, the first forecast distance for this project will be used.
            Only available for time series projects.

        Returns
        -------
        metadata : AccuracyOverTimePlotsMetadata
            a :py:class:`AccuracyOverTimePlotsMetadata
            <datarobot.models.datetime_trend_plots.AccuracyOverTimePlotsMetadata>`
            representing Accuracy over Time plots metadata
        """
        params = {"forecastDistance": forecast_distance}
        url = "projects/{}/datetimeModels/{}/accuracyOverTimePlots/metadata/".format(
            self.project_id, self.id
        )
        server_data = self._client.get(url, params=params).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return AccuracyOverTimePlotsMetadata.from_server_data(server_data)

    def _compute_accuracy_over_time_plot_if_not_computed(
        self, backtest, source, forecast_distance, max_wait
    ):
        metadata = self.get_accuracy_over_time_plots_metadata(forecast_distance=forecast_distance)
        if metadata._get_status(backtest, source) == DATETIME_TREND_PLOTS_STATUS.NOT_COMPLETED:
            job = self.compute_datetime_trend_plots(
                backtest=backtest,
                source=source,
                forecast_distance_start=forecast_distance,
                forecast_distance_end=forecast_distance,
            )
            job.wait_for_completion(max_wait=max_wait)

    def get_accuracy_over_time_plot(
        self,
        backtest=0,
        source=SOURCE_TYPE.VALIDATION,
        forecast_distance=None,
        series_id=None,
        resolution=None,
        max_bin_size=None,
        start_date=None,
        end_date=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Accuracy over Time plots for this model.

        .. versionadded:: v2.25

        Parameters
        ----------
        backtest : int or string, optional
            Retrieve plots for a specific backtest (use the backtest index starting from zero).
            To retrieve plots for holdout, use ``dr.enums.DATA_SUBSET.HOLDOUT``
        source : string, optional
            The source of the data for the backtest/holdout.
            Attribute must be one of ``dr.enums.SOURCE_TYPE``
        forecast_distance : int, optional
            Forecast distance to retrieve the plots for.
            If not specified, the first forecast distance for this project will be used.
            Only available for time series projects.
        series_id : string, optional
            The name of the series to retrieve for multiseries projects.
            If not provided an average plot for the first 1000 series will be retrieved.
        resolution : string, optional
            Specifying at which resolution the data should be binned.
            If not provided an optimal resolution will be used to
            build chart data with number of bins <= ``max_bin_size``.
            One of ``dr.enums.DATETIME_TREND_PLOTS_RESOLUTION``.
        max_bin_size : int, optional
            An int between ``1`` and ``1000``, which specifies
            the maximum number of bins for the retrieval. Default is ``500``.
        start_date : datetime.datetime, optional
            The start of the date range to return.
            If not specified, start date for requested plot will be used.
        end_date : datetime.datetime, optional
            The end of the date range to return.
            If not specified, end date for requested plot will be used.
        max_wait : int or None, optional
            The maximum time to wait for a compute job to complete before retrieving the plots.
            Default is ``dr.enums.DEFAULT_MAX_WAIT``.
            If ``0`` or ``None``, the plots would be retrieved without attempting the computation.

        Returns
        -------
        plot : AccuracyOverTimePlot
            a :py:class:`AccuracyOverTimePlot
            <datarobot.models.datetime_trend_plots.AccuracyOverTimePlot>`
            representing Accuracy over Time plot

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            import pandas as pd
            model = dr.DatetimeModel(project_id=project_id, id=model_id)
            plot = model.get_accuracy_over_time_plot()
            df = pd.DataFrame.from_dict(plot.bins)
            figure = df.plot("start_date", ["actual", "predicted"]).get_figure()
            figure.savefig("accuracy_over_time.png")
        """
        if max_wait:
            self._compute_accuracy_over_time_plot_if_not_computed(
                backtest, source, forecast_distance, max_wait
            )

        params = {
            "backtest": backtest,
            "source": source,
            "forecastDistance": forecast_distance,
            "seriesId": series_id,
            "resolution": resolution,
            "maxBinSize": max_bin_size,
        }

        if start_date:
            if not isinstance(start_date, datetime):
                raise ValueError("start_date must be an instance of datetime.datetime")
            params["startDate"] = datetime_to_string(start_date, ensure_rfc_3339=True)

        if end_date:
            if not isinstance(end_date, datetime):
                raise ValueError("end_date must be an instance of datetime.datetime")
            params["endDate"] = datetime_to_string(end_date, ensure_rfc_3339=True)

        url = "projects/{}/datetimeModels/{}/accuracyOverTimePlots/".format(
            self.project_id, self.id
        )
        server_data = self._client.get(url, params=params).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return AccuracyOverTimePlot.from_server_data(server_data)

    def get_accuracy_over_time_plot_preview(
        self,
        backtest=0,
        source=SOURCE_TYPE.VALIDATION,
        forecast_distance=None,
        series_id=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Accuracy over Time preview plots for this model.

        .. versionadded:: v2.25

        Parameters
        ----------
        backtest : int or string, optional
            Retrieve plots for a specific backtest (use the backtest index starting from zero).
            To retrieve plots for holdout, use ``dr.enums.DATA_SUBSET.HOLDOUT``
        source : string, optional
            The source of the data for the backtest/holdout.
            Attribute must be one of ``dr.enums.SOURCE_TYPE``
        forecast_distance : int, optional
            Forecast distance to retrieve the plots for.
            If not specified, the first forecast distance for this project will be used.
            Only available for time series projects.
        series_id : string, optional
            The name of the series to retrieve for multiseries projects.
            If not provided an average plot for the first 1000 series will be retrieved.
        max_wait : int or None, optional
            The maximum time to wait for a compute job to complete before retrieving the plots.
            Default is ``dr.enums.DEFAULT_MAX_WAIT``.
            If ``0`` or ``None``, the plots would be retrieved without attempting the computation.

        Returns
        -------
        plot : AccuracyOverTimePlotPreview
            a :py:class:`AccuracyOverTimePlotPreview
            <datarobot.models.datetime_trend_plots.AccuracyOverTimePlotPreview>`
            representing Accuracy over Time plot preview

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            import pandas as pd
            model = dr.DatetimeModel(project_id=project_id, id=model_id)
            plot = model.get_accuracy_over_time_plot_preview()
            df = pd.DataFrame.from_dict(plot.bins)
            figure = df.plot("start_date", ["actual", "predicted"]).get_figure()
            figure.savefig("accuracy_over_time_preview.png")
        """
        if max_wait:
            self._compute_accuracy_over_time_plot_if_not_computed(
                backtest, source, forecast_distance, max_wait
            )

        params = {
            "backtest": backtest,
            "source": source,
            "forecastDistance": forecast_distance,
            "seriesId": series_id,
        }

        url = "projects/{}/datetimeModels/{}/accuracyOverTimePlots/preview/".format(
            self.project_id, self.id
        )

        server_data = self._client.get(url, params=params).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return AccuracyOverTimePlotPreview.from_server_data(server_data)

    def get_forecast_vs_actual_plots_metadata(self):
        """
        Retrieve Forecast vs Actual plots metadata for this model.

        .. versionadded:: v2.25

        Returns
        -------
        metadata : ForecastVsActualPlotsMetadata
            a :py:class:`ForecastVsActualPlotsMetadata
            <datarobot.models.datetime_trend_plots.ForecastVsActualPlotsMetadata>`
            representing Forecast vs Actual plots metadata
        """
        url = "projects/{}/datetimeModels/{}/forecastVsActualPlots/metadata/".format(
            self.project_id, self.id
        )
        server_data = self._client.get(url, params={}).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return ForecastVsActualPlotsMetadata.from_server_data(server_data)

    def _compute_forecast_vs_actual_plot_if_not_computed(
        self, backtest, source, forecast_distance_start, forecast_distance_end, max_wait
    ):
        metadata = self.get_forecast_vs_actual_plots_metadata()
        status = metadata._get_status(backtest, source)
        if not status or DATETIME_TREND_PLOTS_STATUS.NOT_COMPLETED not in status:
            return
        for forecast_distance in status[DATETIME_TREND_PLOTS_STATUS.NOT_COMPLETED]:
            if (
                forecast_distance_start is None or forecast_distance >= forecast_distance_start
            ) and (forecast_distance_end is None or forecast_distance <= forecast_distance_end):
                job = self.compute_datetime_trend_plots(
                    backtest=backtest,
                    source=source,
                    forecast_distance_start=forecast_distance_start,
                    forecast_distance_end=forecast_distance_end,
                )
                job.wait_for_completion(max_wait=max_wait)
                break

    def get_forecast_vs_actual_plot(
        self,
        backtest=0,
        source=SOURCE_TYPE.VALIDATION,
        forecast_distance_start=None,
        forecast_distance_end=None,
        series_id=None,
        resolution=None,
        max_bin_size=None,
        start_date=None,
        end_date=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Forecast vs Actual plots for this model.

        .. versionadded:: v2.25

        Parameters
        ----------
        backtest : int or string, optional
            Retrieve plots for a specific backtest (use the backtest index starting from zero).
            To retrieve plots for holdout, use ``dr.enums.DATA_SUBSET.HOLDOUT``
        source : string, optional
            The source of the data for the backtest/holdout.
            Attribute must be one of ``dr.enums.SOURCE_TYPE``
        forecast_distance_start : int, optional:
            The start of forecast distance range (forecast window) to retrieve.
            If not specified, the first forecast distance for this project will be used.
        forecast_distance_end : int, optional:
            The end of forecast distance range (forecast window) to retrieve.
            If not specified, the last forecast distance for this project will be used.
        series_id : string, optional
            The name of the series to retrieve for multiseries projects.
            If not provided an average plot for the first 1000 series will be retrieved.
        resolution : string, optional
            Specifying at which resolution the data should be binned.
            If not provided an optimal resolution will be used to
            build chart data with number of bins <= ``max_bin_size``.
            One of ``dr.enums.DATETIME_TREND_PLOTS_RESOLUTION``.
        max_bin_size : int, optional
            An int between ``1`` and ``1000``, which specifies
            the maximum number of bins for the retrieval. Default is ``500``.
        start_date : datetime.datetime, optional
            The start of the date range to return.
            If not specified, start date for requested plot will be used.
        end_date : datetime.datetime, optional
            The end of the date range to return.
            If not specified, end date for requested plot will be used.
        max_wait : int or None, optional
            The maximum time to wait for a compute job to complete before retrieving the plots.
            Default is ``dr.enums.DEFAULT_MAX_WAIT``.
            If ``0`` or ``None``, the plots would be retrieved without attempting the computation.

        Returns
        -------
        plot : ForecastVsActualPlot
            a :py:class:`ForecastVsActualPlot
            <datarobot.models.datetime_trend_plots.ForecastVsActualPlot>`
            representing Forecast vs Actual plot

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            import pandas as pd
            import matplotlib.pyplot as plt

            model = dr.DatetimeModel(project_id=project_id, id=model_id)
            plot = model.get_forecast_vs_actual_plot()
            df = pd.DataFrame.from_dict(plot.bins)

            # As an example, get the forecasts for the 10th point
            forecast_point_index = 10
            # Pad the forecasts for plotting. The forecasts length must match the df length
            forecasts = [None] * forecast_point_index + df.forecasts[forecast_point_index]
            forecasts = forecasts + [None] * (len(df) - len(forecasts))

            plt.plot(df.start_date, df.actual, label="Actual")
            plt.plot(df.start_date, forecasts, label="Forecast")
            forecast_point = df.start_date[forecast_point_index]
            plt.title("Forecast vs Actual (Forecast Point {})".format(forecast_point))
            plt.legend()
            plt.savefig("forecast_vs_actual.png")
        """
        if max_wait:
            self._compute_forecast_vs_actual_plot_if_not_computed(
                backtest, source, forecast_distance_start, forecast_distance_end, max_wait
            )

        params = {
            "backtest": backtest,
            "source": source,
            "forecastDistanceStart": forecast_distance_start,
            "forecastDistanceEnd": forecast_distance_end,
            "seriesId": series_id,
            "resolution": resolution,
            "maxBinSize": max_bin_size,
        }

        if start_date:
            if not isinstance(start_date, datetime):
                raise ValueError("start_date must be an instance of datetime.datetime")
            params["startDate"] = datetime_to_string(start_date, ensure_rfc_3339=True)

        if end_date:
            if not isinstance(end_date, datetime):
                raise ValueError("end_date must be an instance of datetime.datetime")
            params["endDate"] = datetime_to_string(end_date, ensure_rfc_3339=True)

        url = "projects/{}/datetimeModels/{}/forecastVsActualPlots/".format(
            self.project_id, self.id
        )
        server_data = self._client.get(url, params=params).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return ForecastVsActualPlot.from_server_data(server_data)

    def get_forecast_vs_actual_plot_preview(
        self, backtest=0, source=SOURCE_TYPE.VALIDATION, series_id=None, max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Forecast vs Actual preview plots for this model.

        .. versionadded:: v2.25

        Parameters
        ----------
        backtest : int or string, optional
            Retrieve plots for a specific backtest (use the backtest index starting from zero).
            To retrieve plots for holdout, use ``dr.enums.DATA_SUBSET.HOLDOUT``
        source : string, optional
            The source of the data for the backtest/holdout.
            Attribute must be one of ``dr.enums.SOURCE_TYPE``
        series_id : string, optional
            The name of the series to retrieve for multiseries projects.
            If not provided an average plot for the first 1000 series will be retrieved.
        max_wait : int or None, optional
            The maximum time to wait for a compute job to complete before retrieving the plots.
            Default is ``dr.enums.DEFAULT_MAX_WAIT``.
            If ``0`` or ``None``, the plots would be retrieved without attempting the computation.

        Returns
        -------
        plot : ForecastVsActualPlotPreview
            a :py:class:`ForecastVsActualPlotPreview
            <datarobot.models.datetime_trend_plots.ForecastVsActualPlotPreview>`
            representing Forecast vs Actual plot preview

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            import pandas as pd
            model = dr.DatetimeModel(project_id=project_id, id=model_id)
            plot = model.get_forecast_vs_actual_plot_preview()
            df = pd.DataFrame.from_dict(plot.bins)
            figure = df.plot("start_date", ["actual", "predicted"]).get_figure()
            figure.savefig("forecast_vs_actual_preview.png")
        """
        if max_wait:
            self._compute_forecast_vs_actual_plot_if_not_computed(
                backtest, source, None, None, max_wait
            )

        params = {
            "backtest": backtest,
            "source": source,
            "seriesId": series_id,
        }

        url = "projects/{}/datetimeModels/{}/forecastVsActualPlots/preview/".format(
            self.project_id, self.id
        )

        server_data = self._client.get(url, params=params).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return ForecastVsActualPlotPreview.from_server_data(server_data)

    def get_anomaly_over_time_plots_metadata(self):
        """
        Retrieve Anomaly over Time plots metadata for this model.

        .. versionadded:: v2.25

        Returns
        -------
        metadata : AnomalyOverTimePlotsMetadata
            a :py:class:`AnomalyOverTimePlotsMetadata
            <datarobot.models.datetime_trend_plots.AnomalyOverTimePlotsMetadata>`
            representing Anomaly over Time plots metadata
        """
        url = "projects/{}/datetimeModels/{}/anomalyOverTimePlots/metadata/".format(
            self.project_id, self.id
        )
        server_data = self._client.get(url, params={}).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return AnomalyOverTimePlotsMetadata.from_server_data(server_data)

    def _compute_anomaly_over_time_plot_if_not_computed(self, backtest, source, max_wait):
        metadata = self.get_anomaly_over_time_plots_metadata()
        if metadata._get_status(backtest, source) == DATETIME_TREND_PLOTS_STATUS.NOT_COMPLETED:
            job = self.compute_datetime_trend_plots(backtest=backtest, source=source)
            job.wait_for_completion(max_wait=max_wait)

    def get_anomaly_over_time_plot(
        self,
        backtest=0,
        source=SOURCE_TYPE.VALIDATION,
        series_id=None,
        resolution=None,
        max_bin_size=None,
        start_date=None,
        end_date=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Anomaly over Time plots for this model.

        .. versionadded:: v2.25

        Parameters
        ----------
        backtest : int or string, optional
            Retrieve plots for a specific backtest (use the backtest index starting from zero).
            To retrieve plots for holdout, use ``dr.enums.DATA_SUBSET.HOLDOUT``
        source : string, optional
            The source of the data for the backtest/holdout.
            Attribute must be one of ``dr.enums.SOURCE_TYPE``
        series_id : string, optional
            The name of the series to retrieve for multiseries projects.
            If not provided an average plot for the first 1000 series will be retrieved.
        resolution : string, optional
            Specifying at which resolution the data should be binned.
            If not provided an optimal resolution will be used to
            build chart data with number of bins <= ``max_bin_size``.
            One of ``dr.enums.DATETIME_TREND_PLOTS_RESOLUTION``.
        max_bin_size : int, optional
            An int between ``1`` and ``1000``, which specifies
            the maximum number of bins for the retrieval. Default is ``500``.
        start_date : datetime.datetime, optional
            The start of the date range to return.
            If not specified, start date for requested plot will be used.
        end_date : datetime.datetime, optional
            The end of the date range to return.
            If not specified, end date for requested plot will be used.
        max_wait : int or None, optional
            The maximum time to wait for a compute job to complete before retrieving the plots.
            Default is ``dr.enums.DEFAULT_MAX_WAIT``.
            If ``0`` or ``None``, the plots would be retrieved without attempting the computation.

        Returns
        -------
        plot : AnomalyOverTimePlot
            a :py:class:`AnomalyOverTimePlot
            <datarobot.models.datetime_trend_plots.AnomalyOverTimePlot>`
            representing Anomaly over Time plot

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            import pandas as pd
            model = dr.DatetimeModel(project_id=project_id, id=model_id)
            plot = model.get_anomaly_over_time_plot()
            df = pd.DataFrame.from_dict(plot.bins)
            figure = df.plot("start_date", "predicted").get_figure()
            figure.savefig("anomaly_over_time.png")
        """
        if max_wait:
            self._compute_anomaly_over_time_plot_if_not_computed(backtest, source, max_wait)

        params = {
            "backtest": backtest,
            "source": source,
            "seriesId": series_id,
            "resolution": resolution,
            "maxBinSize": max_bin_size,
        }

        if start_date:
            if not isinstance(start_date, datetime):
                raise ValueError("start_date must be an instance of datetime.datetime")
            params["startDate"] = datetime_to_string(start_date, ensure_rfc_3339=True)

        if end_date:
            if not isinstance(end_date, datetime):
                raise ValueError("end_date must be an instance of datetime.datetime")
            params["endDate"] = datetime_to_string(end_date, ensure_rfc_3339=True)

        url = "projects/{}/datetimeModels/{}/anomalyOverTimePlots/".format(self.project_id, self.id)
        server_data = self._client.get(url, params=params).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return AnomalyOverTimePlot.from_server_data(server_data)

    def get_anomaly_over_time_plot_preview(
        self,
        prediction_threshold=0.5,
        backtest=0,
        source=SOURCE_TYPE.VALIDATION,
        series_id=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Retrieve Anomaly over Time preview plots for this model.

        .. versionadded:: v2.25

        Parameters
        ----------
        prediction_threshold: float, optional
            Only bins with predictions exceeding this threshold will be returned in the response.
        backtest : int or string, optional
            Retrieve plots for a specific backtest (use the backtest index starting from zero).
            To retrieve plots for holdout, use ``dr.enums.DATA_SUBSET.HOLDOUT``
        source : string, optional
            The source of the data for the backtest/holdout.
            Attribute must be one of ``dr.enums.SOURCE_TYPE``
        series_id : string, optional
            The name of the series to retrieve for multiseries projects.
            If not provided an average plot for the first 1000 series will be retrieved.
        max_wait : int or None, optional
            The maximum time to wait for a compute job to complete before retrieving the plots.
            Default is ``dr.enums.DEFAULT_MAX_WAIT``.
            If ``0`` or ``None``, the plots would be retrieved without attempting the computation.

        Returns
        -------
        plot : AnomalyOverTimePlotPreview
            a :py:class:`AnomalyOverTimePlotPreview
            <datarobot.models.datetime_trend_plots.AnomalyOverTimePlotPreview>`
            representing Anomaly over Time plot preview

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            import pandas as pd
            import matplotlib.pyplot as plt

            model = dr.DatetimeModel(project_id=project_id, id=model_id)
            plot = model.get_anomaly_over_time_plot_preview(prediction_threshold=0.01)
            df = pd.DataFrame.from_dict(plot.bins)
            x = pd.date_range(
                plot.start_date, plot.end_date, freq=df.end_date[0] - df.start_date[0]
            )
            plt.plot(x, [0] * len(x), label="Date range")
            plt.plot(df.start_date, [0] * len(df.start_date), "ro", label="Anomaly")
            plt.yticks([])
            plt.legend()
            plt.savefig("anomaly_over_time_preview.png")
        """
        if max_wait:
            self._compute_anomaly_over_time_plot_if_not_computed(backtest, source, max_wait)

        params = {
            "predictionThreshold": prediction_threshold,
            "backtest": backtest,
            "source": source,
            "seriesId": series_id,
        }

        url = "projects/{}/datetimeModels/{}/anomalyOverTimePlots/preview/".format(
            self.project_id, self.id
        )

        server_data = self._client.get(url, params=params).json()
        server_data["projectId"] = self.project_id
        server_data["modelId"] = self.id
        return AnomalyOverTimePlotPreview.from_server_data(server_data)

    def initialize_anomaly_assessment(self, backtest, source, series_id=None):
        """Initialize the anomaly assessment insight and calculate
        Shapley explanations for the most anomalous points in the subset.
        The insight is available for anomaly detection models in time series unsupervised projects
        which also support calculation of Shapley values.

        Parameters
        ----------
        backtest: int starting with 0 or "holdout"
            The backtest to compute insight for.
        source: "training" or "validation"
            The source to compute insight for.
        series_id: string
            Required for multiseries projects. The series id to compute insight for.
            Say if there is a series column containing cities,
            the example of the series name to pass would be "Boston"

        Returns
        -------
        AnomalyAssessmentRecord

        """
        return AnomalyAssessmentRecord.compute(
            self.project_id, self.id, backtest, source, series_id=series_id
        )

    def get_anomaly_assessment_records(
        self, backtest=None, source=None, series_id=None, limit=100, offset=0, with_data_only=False
    ):
        """
        Retrieve computed Anomaly Assessment records for this model. Model must be an anomaly
        detection model in time series unsupervised project which also supports calculation of
        Shapley values.

        Records can be filtered by the data backtest, source and series_id.
        The results can be limited.

        .. versionadded:: v2.25

        Parameters
        ----------
        backtest: int starting with 0 or "holdout"
            The backtest of the data to filter records by.
        source: "training" or "validation"
            The source of the data to filter records by.
        series_id: string
            The series id to filter records by.
        limit: int, optional
        offset: int, optional
        with_data_only: bool, optional
            Whether to return only records with preview and explanations available.
            False by default.

        Returns
        -------
        records : list of AnomalyAssessmentRecord
            a :py:class:`AnomalyAssessmentRecord
            <datarobot.models.anomaly_assessment.AnomalyAssessmentRecord>`
            representing Anomaly Assessment Record

        """
        return AnomalyAssessmentRecord.list(
            self.project_id,
            self.id,
            backtest=backtest,
            source=source,
            series_id=series_id,
            limit=limit,
            offset=offset,
            with_data_only=with_data_only,
        )


class RatingTableModel(Model):
    """A model that has a rating table.

    All durations are specified with a duration string such as those returned
    by the :meth:`partitioning_methods.construct_duration_string
    <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
    Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
    for more information on duration strings.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float or None
        the percentage of the project dataset used in training the model.  If the project uses
        datetime partitioning, the sample_pct will be None.  See `training_row_count`,
        `training_duration`, and `training_start_date` and `training_end_date` instead.
    training_row_count : int or None
        the number of rows of the project dataset used in training the model.  In a datetime
        partitioned project, if specified, defines the number of rows used to train the model and
        evaluate backtest scores; if unspecified, either `training_duration` or
        `training_start_date` and `training_end_date` was used to determine that instead.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    rating_table_id : str
        the id of the rating table that belongs to this model
    monotonic_increasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically increasing relationship to the target.
        If None, no such constraints are enforced.
    monotonic_decreasing_featurelist_id : str
        optional, the id of the featurelist that defines the set of features with
        a monotonically decreasing relationship to the target.
        If None, no such constraints are enforced.
    supports_monotonic_constraints : bool
        optional, whether this model supports enforcing monotonic constraints
    is_starred : bool
        whether this model marked as starred
    prediction_threshold : float
        for binary classification projects, the threshold used for predictions
    prediction_threshold_read_only : bool
        indicated whether modification of the prediction threshold is forbidden. Threshold
        modification is forbidden once a model has had a deployment created or predictions made via
        the dedicated prediction API.
    model_number : integer
        model number assigned to a model
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this model is supported in the Composable ML.
    """

    _converter = (t.Dict({t.Key("rating_table_id"): String}) + Model._converter).allow_extra("*")

    def __init__(
        self,
        id=None,
        processes=None,
        featurelist_name=None,
        featurelist_id=None,
        project_id=None,
        sample_pct=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        model_type=None,
        model_category=None,
        is_frozen=None,
        blueprint_id=None,
        metrics=None,
        rating_table_id=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        supports_monotonic_constraints=None,
        is_starred=None,
        prediction_threshold=None,
        prediction_threshold_read_only=None,
        model_number=None,
        supports_composable_ml=None,
    ):
        super(RatingTableModel, self).__init__(
            id=id,
            processes=processes,
            featurelist_name=featurelist_name,
            featurelist_id=featurelist_id,
            project_id=project_id,
            sample_pct=sample_pct,
            training_row_count=training_row_count,
            training_duration=training_duration,
            training_start_date=training_start_date,
            training_end_date=training_end_date,
            model_type=model_type,
            model_category=model_category,
            is_frozen=is_frozen,
            blueprint_id=blueprint_id,
            metrics=metrics,
            monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
            monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
            supports_monotonic_constraints=supports_monotonic_constraints,
            is_starred=is_starred,
            prediction_threshold=prediction_threshold,
            prediction_threshold_read_only=prediction_threshold_read_only,
            model_number=model_number,
            supports_composable_ml=supports_composable_ml,
        )
        self.rating_table_id = rating_table_id

    def __repr__(self):
        return "RatingTableModel({!r})".format(self.model_type or self.id)

    @classmethod
    def get(cls, project_id, model_id):
        """Retrieve a specific rating table model

        If the project does not have a rating table, a ClientError will occur.

        Parameters
        ----------
        project_id : str
            the id of the project the model belongs to
        model_id : str
            the id of the model to retrieve

        Returns
        -------
        model : RatingTableModel
            the model
        """
        url = "projects/{}/ratingTableModels/{}/".format(project_id, model_id)
        return cls.from_location(url)

    @classmethod
    def create_from_rating_table(cls, project_id, rating_table_id):
        """
        Creates a new model from a validated rating table record. The
        RatingTable must not be associated with an existing model.

        Parameters
        ----------
        project_id : str
            the id of the project the rating table belongs to
        rating_table_id : str
            the id of the rating table to create this model from

        Returns
        -------
        job: Job
            an instance of created async job

        Raises
        ------
        ClientError (422)
            Raised if creating model from a RatingTable that failed validation
        JobAlreadyRequested
            Raised if creating model from a RatingTable that is already
            associated with a RatingTableModel
        """
        from .job import Job

        path = "projects/{}/ratingTableModels/".format(project_id)
        payload = {"rating_table_id": rating_table_id}
        response = cls._client.post(path, data=payload)
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)


class ModelParameters(APIObject):
    """Model parameters information provides the data needed to reproduce
    predictions for a selected model.

    Attributes
    ----------
    parameters : list of dict
        Model parameters that are related to the whole model.
    derived_features : list of dict
        Preprocessing information about derived features, including original feature name, derived
        feature name, feature type, list of applied transformation and coefficient for the
        derived feature. Multistage models also contains list of coefficients for each stage in
        `stage_coefficients` key (empty list for single stage models).

    Notes
    -----
    For additional information see DataRobot web application documentation, section
    "Coefficients tab and pre-processing details"
    """

    _converter = t.Dict(
        {
            t.Key("parameters"): t.List(
                t.Dict({t.Key("name"): String, t.Key("value"): t.Any}).ignore_extra("*")
            ),
            t.Key("derived_features"): t.List(
                t.Dict(
                    {
                        t.Key("coefficient"): t.Float,
                        t.Key("stage_coefficients", default=[]): t.List(
                            t.Dict(
                                {t.Key("stage"): String, t.Key("coefficient"): t.Float}
                            ).ignore_extra("*")
                        ),
                        t.Key("derived_feature"): String,
                        t.Key("original_feature"): String,
                        t.Key("type"): String,
                        t.Key("transformations"): t.List(
                            t.Dict({t.Key("name"): String, t.Key("value"): t.Any}).ignore_extra("*")
                        ),
                    }
                ).ignore_extra("*")
            ),
        }
    ).ignore_extra("*")

    def __init__(self, parameters=None, derived_features=None):
        self.parameters = parameters
        self.derived_features = derived_features

    def __repr__(self):
        out = u"ModelParameters({} parameters, {} features)".format(
            len(self.parameters), len(self.derived_features)
        )
        return encode_utf8_if_py2(out)

    @classmethod
    def get(cls, project_id, model_id):
        """Retrieve model parameters.

        Parameters
        ----------
        project_id : str
            The project's id.
        model_id : str
            Id of model parameters we requested.

        Returns
        -------
        ModelParameters
            The queried model parameters.
        """
        url = "projects/{}/models/{}/parameters/".format(project_id, model_id)
        return cls.from_location(url)


class ClusteringModel(Model):
    """
    ClusteringModel extends :class:`Model<datarobot.models.Model>` class.
    It provides provides properties and methods specific to clustering projects.
    """

    def compute_insights(self, max_wait=DEFAULT_MAX_WAIT):
        """
        Compute and retrieve cluster insights for model. This method awaits completion of
        job computing cluster insights and returns results after it is finished. If computation
        takes longer than specified ``max_wait`` exception will be raised.

        Parameters
        ----------
        project_id: str
            Project to start creation in.
        model_id: str
            Project's model to start creation in.
        max_wait: int
            Maximum number of seconds to wait before giving up

        Returns
        -------
        List of ClusterInsight

        Raises
        ------
        ClientError
            Server rejected creation due to client error.
            Most likely cause is bad ``project_id`` or ``model_id``.
        AsyncFailureError
            If any of the responses from the server are unexpected
        AsyncProcessUnsuccessfulError
            If the cluster insights computation has failed or was cancelled.
        AsyncTimeoutError
            If the cluster insights computation did not resolve in time
        """
        return ClusterInsight.compute(
            project_id=self.project_id, model_id=self.id, max_wait=max_wait
        )

    @property
    def insights(self):
        """Return actual list of cluster insights if already computed.

        Returns
        -------
        List of ClusterInsight
        """
        return ClusterInsight.list(project_id=self.project_id, model_id=self.id)

    @property
    def clusters(self):
        """Return actual list of Clusters.

        Returns
        -------
        List of Cluster
        """
        return Cluster.list(project_id=self.project_id, model_id=self.id)

    def update_cluster_names(self, cluster_name_mappings):
        """Change many cluster names at once based on list of name mappings.

        Parameters
        ----------
        cluster_name_mappings: List of tuples
            Cluster names mapping consisting of current cluster name and old cluster name.
            Example:

            .. code-block:: python

                cluster_name_mappings = [
                    ("current cluster name 1", "new cluster name 1"),
                    ("current cluster name 2", "new cluster name 2")]

        Returns
        -------
        List of Cluster

        Raises
        ------
        datarobot.errors.ClientError
            Server rejected update of cluster names.
            Possible reasons include: incorrect format of mapping, mapping introduces duplicates.
        """
        return Cluster.update_multiple_names(
            project_id=self.project_id,
            model_id=self.id,
            cluster_name_mappings=cluster_name_mappings,
        )

    def update_cluster_name(self, current_name, new_name):
        """Change cluster name from current_name to new_name.

        Parameters
        ----------
        current_name: str
            Current cluster name.
        new_name: str
            New cluster name.

        Returns
        -------
        List of Cluster

        Raises
        ------
        datarobot.errors.ClientError
            Server rejected update of cluster names.
        """
        return Cluster.update_name(
            project_id=self.project_id,
            model_id=self.id,
            current_name=current_name,
            new_name=new_name,
        )


class CombinedModel(Model):
    """
    A model from a segmented project. Combination of ordinary models in child segments projects.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    segmentation_task_id : str
        the id of a segmentation task used in this model
    """

    _converter = t.Dict(
        {
            t.Key("combined_model_id") >> "id": t.String,
            t.Key("project_id"): t.String,
            t.Key("segmentation_task_id"): t.String,
        }
    ).ignore_extra("*")

    # noinspection PyMissingConstructor
    def __init__(self, id=None, project_id=None, segmentation_task_id=None):
        self.id = id
        self.project_id = project_id
        self.segmentation_task_id = segmentation_task_id

        # Private attributes.
        self._base_model_path = self._base_model_path_template.format(self.project_id)

    def __repr__(self):
        return "CombinedModel({})".format(self.id)

    @classmethod
    def get(cls, project_id, combined_model_id):
        """ Retrieve combined model

        Parameters
        ----------
        project_id : str
            The project's id.
        combined_model_id : str
            Id of the combined model.

        Returns
        -------
        CombinedModel
            The queried combined model.
        """
        url = "projects/{}/combinedModels/{}/".format(project_id, combined_model_id)
        return cls.from_location(url)

    @classmethod
    def set_segment_champion(cls, project_id, model_id):
        """ Update a segment champion in a combined model by setting the model_id
        that belongs to the child project_id as the champion.

        Parameters
        ----------
        project_id : str
            The project id for the child model that contains the model id.
        model_id : str
            Id of the model to mark as the champion

        Returns
        -------
        combined_model_id : str
            Id of the combined model that was updated

        """
        url = "projects/{}/segmentChampion/".format(project_id)
        response = cls._client.put(url, json={"modelId": model_id})
        return response.json().get("combinedModelId")

    def get_segments_info(self):
        """Retrieve Combined Model segments info

        Returns
        -------
        list[SegmentInfo]
            List of segments
        """
        return SegmentInfo.list(self.project_id, self.id)

    def get_segments_as_dataframe(self, encoding="utf-8"):
        """ Retrieve Combine Models segments as a DataFrame.

        Parameters
        ----------
        encoding : str, optional
            A string representing the encoding to use in the output csv file.
            Defaults to 'utf-8'.

        Returns
        -------
        DataFrame
            Combined model segments
        """
        path = "projects/{}/combinedModels/{}/segments/download/".format(self.project_id, self.id)
        resp = self._client.get(path, headers={"Accept": "text/csv"}, stream=True)
        if resp.status_code == 200:
            content = resp.content.decode("utf-8")
            return pd.read_csv(six.StringIO(content), index_col=0, encoding=encoding)
        else:
            raise ServerError(
                "Server returned unknown status code: {}".format(resp.status_code),
                resp.status_code,
            )

    def get_segments_as_csv(self, filename, encoding="utf-8"):
        """ Save the Combine Models segments to a csv.

        Parameters
        ----------
        filename : str or file object
            The path or file object to save the data to.
        encoding : str, optional
            A string representing the encoding to use in the output csv file.
            Defaults to 'utf-8'.
        """
        data = self.get_segments_as_dataframe(encoding=encoding)
        data.to_csv(
            path_or_buf=filename, header=True, index=False, encoding=encoding,
        )

    def train(
        self,
        sample_pct=None,
        featurelist_id=None,
        scoring_type=None,
        training_row_count=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
    ):
        """ Inherited from Model - CombinedModels cannot be retrained directly """
        raise NotImplementedError("CombinedModels cannot be retrained")

    def train_datetime(
        self,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        time_window_sample_pct=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        use_project_settings=False,
        sampling_method=None,
    ):
        """ Inherited from Model - CombinedModels cannot be retrained directly """
        raise NotImplementedError("CombinedModels cannot be retrained")

    def retrain(
        self,
        time_window_sample_pct=None,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        sampling_method=None,
    ):
        """ Inherited from Model - CombinedModels cannot be retrained directly """
        raise NotImplementedError("CombinedModels cannot be retrained")

    def request_frozen_model(self, sample_pct=None, training_row_count=None):
        """ Inherited from Model - CombinedModels cannot be retrained as frozen """
        raise NotImplementedError("CombinedModels cannot be retrained as frozen")

    def request_frozen_datetime_model(
        self,
        training_row_count=None,
        training_duration=None,
        training_start_date=None,
        training_end_date=None,
        time_window_sample_pct=None,
        sampling_method=None,
    ):
        """ Inherited from Model - CombinedModels cannot be retrained as frozen """
        raise NotImplementedError("CombinedModels cannot be retrained as frozen")

    def cross_validate(self):
        """ Inherited from Model - CombinedModels cannot request cross validation """
        raise NotImplementedError("CombinedModels cannot request cross validation")
