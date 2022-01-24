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
from datarobot.enums import FEATURE_TYPE
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2, from_api, get_id_from_response
from datarobot.utils.pagination import unpaginate


class FeatureEffectMetadata(APIObject):
    """ Feature Effect Metadata for model, contains status and available model sources.

    Notes
    -----

    `source` is expected parameter to retrieve Feature Fit. One of provided sources
    shall be used.

    """

    _converter = t.Dict({t.Key("status"): String, t.Key("sources"): t.List(String)}).ignore_extra(
        "*"
    )

    def __init__(self, status, sources):
        self.status = status
        self.sources = sources

    def __repr__(self):
        return encode_utf8_if_py2(u"FeatureEffectMetadata({}/{})".format(self.status, self.sources))


class FeatureEffectMetadataDatetime(APIObject):
    """ Feature Effect Metadata for datetime model, contains list of
    feature effect metadata per backtest.

    Notes
    -----
    ``feature effect metadata per backtest`` contains:
        * ``status`` : string.
        * ``backtest_index`` : string.
        * ``sources`` : list(string).

    `source` is expected parameter to retrieve Feature Fit. One of provided sources
    shall be used.

    `backtest_index` is expected parameter to submit compute request and retrieve Feature Effect.
    One of provided backtest indexes shall be used.

    Attributes
    ----------
    data : list[FeatureEffectMetadataDatetimePerBacktest]
        List feature effect metadata per backtest

    """

    _converter = t.Dict(
        {
            t.Key("data"): t.List(
                t.Dict(
                    {
                        t.Key("backtest_index"): String,
                        t.Key("status"): String,
                        t.Key("sources"): t.List(String),
                    }
                ).ignore_extra("*")
            )
        }
    ).ignore_extra("*")

    def __init__(self, data):
        self.data = [
            FeatureEffectMetadataDatetimePerBacktest(fe_meta_per_backtest)
            for fe_meta_per_backtest in data
        ]

    def __repr__(self):
        return encode_utf8_if_py2(u"FeatureEffectDatetimeMetadata({})".format(self.data))

    def __iter__(self):
        return iter(self.data)


class FeatureEffectMetadataDatetimePerBacktest(object):
    """Convert dictionary into feature effect metadata per backtest which contains backtest_index,
    status and sources.
    """

    def __init__(self, ff_metadata_datetime_per_backtest):
        self.backtest_index = ff_metadata_datetime_per_backtest["backtest_index"]
        self.status = ff_metadata_datetime_per_backtest["status"]
        self.sources = ff_metadata_datetime_per_backtest["sources"]

    def __repr__(self):
        return encode_utf8_if_py2(
            u"FeatureEffectMetadataDatetimePerBacktest(backtest_index={},"
            u"status={}, sources={}".format(self.backtest_index, self.status, self.sources)
        )

    def __eq__(self, other):
        return all(
            [
                self.backtest_index == other.backtest_index,
                self.status == other.status,
                sorted(self.sources) == sorted(other.sources),
            ]
        )

    def __lt__(self, other):
        return self.backtest_index < other.backtest_index


class FeatureEffects(APIObject):
    """
    Feature Effects provides partial dependence and predicted vs actual values for top-500
    features ordered by feature impact score.

    The partial dependence shows marginal effect of a feature on the target variable after
    accounting for the average effects of all other predictive features. It indicates how, holding
    all other variables except the feature of interest as they were, the value of this feature
    affects your prediction.

    Attributes
    ----------
    project_id: string
        The project that contains requested model
    model_id: string
        The model to retrieve Feature Effects for
    source: string
        The source to retrieve Feature Effects for
    feature_effects: list
        Feature Effects for every feature
    backtest_index: string, required only for DatetimeModels,
        The backtest index to retrieve Feature Effects for.

    Notes
    ------
    ``featureEffects`` is a dict containing the following:

        * ``feature_name`` (string) Name of the feature
        * ``feature_type`` (string) `dr.enums.FEATURE_TYPE`, \
          Feature type either numeric, categorical or datetime
        * ``feature_impact_score`` (float) Feature impact score
        * ``weight_label`` (string) optional, Weight label if configured for the project else null
        * ``partial_dependence`` (List) Partial dependence results
        * ``predicted_vs_actual`` (List) optional, Predicted versus actual results, \
          may be omitted if there are insufficient qualified samples

    ``partial_dependence`` is a dict containing the following:
        * ``is_capped`` (bool) Indicates whether the data for computation is capped
        * ``data`` (List) partial dependence results in the following format

    ``data`` is a list of dict containing the following:
        * ``label`` (string) Contains label for categorical and numeric features as string
        * ``dependence`` (float) Value of partial dependence

    ``predicted_vs_actual`` is a dict containing the following:
        * ``is_capped`` (bool) Indicates whether the data for computation is capped
        * ``data`` (List) pred vs actual results in the following format

    ``data`` is a list of dict containing the following:
        * ``label`` (string) Contains label for categorical features \
          for numeric features contains range or numeric value.
        * ``bin`` (List) optional, For numeric features contains \
          labels for left and right bin limits
        * ``predicted`` (float) Predicted value
        * ``actual`` (float) Actual value. Actual value is null \
          for unsupervised timeseries models
        * ``row_count`` (int or float) Number of rows for the label and bin. \
          Type is float if weight or exposure is set for the project.
    """

    _PartialDependence = t.Dict(
        {
            t.Key("is_capped"): t.Bool,
            t.Key("data"): t.List(
                t.Dict({t.Key("label"): String | Int, t.Key("dependence"): t.Float}).ignore_extra(
                    "*"
                )
            ),
        }
    ).ignore_extra("*")

    _PredictedVsActual = t.Dict(
        {
            t.Key("is_capped"): t.Bool,
            t.Key("data"): t.List(
                t.Dict(
                    {
                        t.Key("row_count"): Int | t.Float,
                        t.Key("label"): String,
                        t.Key("bin", optional=True): t.List(String),
                        t.Key("predicted"): t.Float | t.Null,
                        t.Key("actual"): t.Float | t.Null,
                    }
                ).ignore_extra("*")
            ),
        }
    ).ignore_extra("*")

    _IndividualConditionalExpectation = t.Dict(
        {
            t.Key("is_capped"): t.Bool,
            t.Key("data"): t.List(
                t.List(
                    t.Dict(
                        {t.Key("label"): String | Int, t.Key("dependence"): t.Float}
                    ).ignore_extra("*")
                )
            ),
        }
    ).ignore_extra("*")

    _FeatureEffect = t.Dict(
        {
            t.Key("feature_name"): String,
            t.Key("feature_impact_score"): t.Float,
            t.Key("feature_type"): t.Enum(
                FEATURE_TYPE.NUMERIC, FEATURE_TYPE.CATEGORICAL, FEATURE_TYPE.DATETIME
            ),
            t.Key("partial_dependence"): _PartialDependence,
            t.Key("predicted_vs_actual", optional=True): _PredictedVsActual,
            t.Key("weight_label", optional=True): String | t.Null,
            t.Key("is_scalable"): t.Bool | t.Null,
            t.Key("is_binnable"): t.Bool,
            t.Key("monotonicity_score", optional=True): t.Float | t.Null,
            t.Key("correlated_with", optional=True): t.List(String),
            t.Key("exclusion_threshold", optional=True): t.Float,
            t.Key(
                "individual_conditional_expectation", optional=True
            ): _IndividualConditionalExpectation,
        }
    ).ignore_extra("*")

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("source"): String,
            t.Key("backtest_index", optional=True): String,
            t.Key("feature_effects"): t.List(_FeatureEffect),
        }
    ).ignore_extra("*")

    def __init__(
        self, project_id, model_id, source, feature_effects, backtest_index=None,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.source = source
        self.backtest_index = backtest_index
        self.feature_effects = feature_effects

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(project_id={},"
            u"model_id={}, source={}, backtest_index={}, feature_effects={}".format(
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                self.source,
                self.backtest_index,
                self.feature_effects,
            )
        )

    def __eq__(self, other):
        return all(
            [
                self.project_id == other.project_id,
                self.model_id == other.model_id,
                self.source == other.source,
                self.backtest_index == other.backtest_index,
                (
                    sorted(self.feature_effects, key=lambda k: k["feature_name"])
                    == sorted(other.feature_effects, key=lambda k: k["feature_name"])
                ),
            ]
        )

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                self.source,
                self.backtest_index,
            )
        )

    def __iter__(self):
        return iter(self.feature_effects)

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
        # keep_null_keys is required for predicted/actual
        case_converted = from_api(data, keep_null_keys=True)
        return cls.from_data(case_converted)


class FeatureEffectsMulticlass(APIObject):
    """
    Feature Effects for a model in multiclass project.

    Attributes
    ----------
    class_ : str
        Name of the class.
    feature_name : str
        Name of the feature.
    feature_type : dr.enums.FEATURE_TYPE
        Feature type either numeric, categorical or datetime.
    feature_impact_score : float
        Feature impact score.
    weight_label : str
        Optional. Weight label if configured for the project else None.
    partial_dependence : list
        Partial dependence results.
    predicted_vs_actual : list
        Optional. Predicted versus actual results, may be omitted if there are insufficient
        qualified samples.
    """

    _path = "projects/{project_id}/{model_type}/{model_id}/multiclassFeatureEffects/"
    _converter = (
        t.Dict({t.Key("class", to_name="class_"): String()})
        .merge(FeatureEffects._FeatureEffect)
        .ignore_extra("*")
    )

    def __init__(
        self,
        class_,
        feature_name,
        feature_type,
        feature_impact_score,
        partial_dependence,
        is_scalable,
        is_binnable,
        predicted_vs_actual=None,
        weight_label=None,
    ):
        self.class_ = class_
        self.feature_name = feature_name
        self.feature_type = feature_type
        self.feature_impact_score = feature_impact_score
        self.partial_dependence = partial_dependence
        self.predicted_vs_actual = predicted_vs_actual
        self.weight_label = weight_label
        self.is_scalable = is_scalable
        self.is_binnable = is_binnable

    def __repr__(self):
        return encode_utf8_if_py2(
            "{}(class={}, feature_name={}, feature_type={}, feature_impact_score={}, "
            "weight_label={}, partial_dependence={}, predicted_vs_actual={})".format(
                self.__class__.__name__,
                self.class_,
                self.feature_name,
                self.feature_type,
                self.feature_impact_score,
                self.weight_label,
                self.partial_dependence,
                self.predicted_vs_actual,
            )
        )

    @classmethod
    def create(
        cls,
        project_id,
        model_id,
        backtest_index=None,
        row_count=None,
        top_n_features=10,
        features=None,
    ):
        """
        Compute feature effects for a multiclass model.

        Parameters
        ----------
        project_id : string
            The project that contains requested model.
        model_id : string
            The model for which to retrieve Feature Effects.
        row_count : int
            The number of rows from dataset to use for Feature Impact calculation.
        backtest_index : str
            The backtest index for datetime models. e.g. 0, 1, ..., 20, holdout, startstop
        top_n_features : int or None
            Number of top features (ranked by Feature Impact) to use to calculate Feature Effects.
        features : list or None
            The list of features used to calculate Feature Effects.

        Returns
        -------
        job : FeatureEffectsMulticlassJob
            A Job representing Feature Effect computation. To get the completed Feature Effect data,
            use `job.get_result` or `job.get_result_when_complete`.
        """
        if not ((features is None) ^ (top_n_features is None)):
            raise ValueError(
                "Either 'features' or 'top_n_features' must be provided, but not both."
            )
        payload = {"rowCount": row_count}
        if backtest_index is not None:
            payload["backtestIndex"] = backtest_index
        if top_n_features:
            payload["topNFeatures"] = top_n_features
        if features:
            payload["features"] = features
        url = cls._get_url(project_id, model_id, backtest_index)
        response = cls._client.post(url, json=payload)
        job_id = get_id_from_response(response)
        from .job import FeatureEffectsMulticlassJob

        return FeatureEffectsMulticlassJob.get(project_id, job_id)

    @classmethod
    def get(cls, project_id, model_id, source="training", backtest_index=None, class_=None):
        """
        Retrieve multiclass Feature Effects.

        Parameters
        ----------
        project_id: str
            project id
        model_id: str
            model id
        source: str
            datasource, optional defaults to 'training' (e.g. 'validation', 'training', 'holdout')
        backtest_index: str
            backtest index, required for datetime models (e.g. 0, 1, ..., 20, holdout, startstop)
        class_: str
            target class name

        Returns
        -------
            list of FeatureEffectsMulticlass
        """

        params = {"source": source}
        if backtest_index is not None:
            params["backtestIndex"] = backtest_index
        if class_:
            params["class"] = class_
        url = cls._get_url(project_id, model_id, backtest_index)
        return cls.from_location(url, params=params)

    @classmethod
    def from_location(cls, path, keep_attrs=None, params=None):
        results = unpaginate(initial_url=path, initial_params=params, client=cls._client)
        return [
            cls.from_data(from_api(item, keep_attrs=keep_attrs, keep_null_keys=True))
            for item in results
        ]

    @classmethod
    def _get_url(cls, project_id, model_id, backtest_index):
        model_type = "models" if backtest_index is None else "datetimeModels"
        url = cls._path.format(project_id=project_id, model_type=model_type, model_id=model_id)
        return url
