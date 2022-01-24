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
from datarobot.models.feature_effect import (
    FeatureEffectMetadata,
    FeatureEffectMetadataDatetime,
    FeatureEffectMetadataDatetimePerBacktest,
)
from datarobot.utils import encode_utf8_if_py2, from_api


class FeatureFitMetadata(FeatureEffectMetadata):
    """ Feature Fit Metadata for model, contains status and available model sources.

    Notes
    -----

    `source` is expected parameter to retrieve Feature Fit. One of provided sources
    shall be used.

    """

    def __repr__(self):
        return encode_utf8_if_py2(u"FeatureFitMetadata({}/{})".format(self.status, self.sources))


class FeatureFitMetadataDatetime(FeatureEffectMetadataDatetime):
    """ Feature Fit Metadata for datetime model, contains list of feature fit metadata per backtest.

    Notes
    -----
    ``feature fit metadata per backtest`` contains:

    * ``status`` : string.
    * ``backtest_index`` : string.
    * ``sources`` : list(string).

    `source` is expected parameter to retrieve Feature Fit. One of provided sources
    shall be used.

    `backtest_index` is expected parameter to submit compute request and retrieve Feature Fit.
    One of provided backtest indexes shall be used.

    Attributes
    ----------
    data : list[FeatureFitMetadataDatetimePerBacktest]
        list feature fit metadata per backtest

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
            FeatureFitMetadataDatetimePerBacktest(ff_meta_per_backtest)
            for ff_meta_per_backtest in data
        ]

    def __repr__(self):
        return encode_utf8_if_py2(u"FeatureFitMetadataDatetime({})".format(self.data))

    def __iter__(self):
        return iter(self.data)


class FeatureFitMetadataDatetimePerBacktest(FeatureEffectMetadataDatetimePerBacktest):
    """Convert dictionary into feature fit metadata per backtest which contains backtest_index,
    status and sources.
    """

    def __repr__(self):
        return encode_utf8_if_py2(
            u"FeatureFitMetadataDatetimePerBacktest(backtest_index={},"
            u"status={}, sources={}".format(self.backtest_index, self.status, self.sources)
        )


class FeatureFit(APIObject):
    """
    Feature Fit provides partial dependence and predicted vs actual values for top-500
    features ordered by feature importance score.

    The partial dependence shows marginal effect of a feature on the target variable after
    accounting for the average effects of all other predictive features. It indicates how, holding
    all other variables except the feature of interest as they were, the value of this feature
    affects your prediction.

    Attributes
    ----------
    project_id: string
        The project that contains requested model
    model_id: string
        The model to retrieve Feature Fit for
    source: string
        The source to retrieve Feature Fit for
    feature_fit: list
        Feature Fit data for every feature
    backtest_index: string, required only for DatetimeModels,
        The backtest index to retrieve Feature Fit for.

    Notes
    ------
    ``featureFit`` is a dict containing the following:

        * ``feature_name`` (string) Name of the feature
        * ``feature_type`` (string) `dr.enums.FEATURE_TYPE`, \
          Feature type either numeric, categorical or datetime
        * ``feature_importance_score`` (float) Feature importance score
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

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("source"): String,
            t.Key("backtest_index", optional=True): String,
            t.Key("feature_fit"): t.List(
                t.Dict(
                    {
                        t.Key("feature_name"): String,
                        t.Key("feature_importance_score"): t.Float,
                        t.Key("feature_type"): t.Enum(
                            FEATURE_TYPE.NUMERIC, FEATURE_TYPE.CATEGORICAL, FEATURE_TYPE.DATETIME
                        ),
                        t.Key("partial_dependence"): _PartialDependence,
                        t.Key("predicted_vs_actual"): _PredictedVsActual,
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
            ),
        }
    ).ignore_extra("*")

    def __init__(
        self, project_id, model_id, source, feature_fit, backtest_index=None,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.source = source
        self.backtest_index = backtest_index
        self.feature_fit = feature_fit

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(project_id={},"
            u"model_id={}, source={}, backtest_index={}, feature_fit={}".format(
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                self.source,
                self.backtest_index,
                self.feature_fit,
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
                    sorted(self.feature_fit, key=lambda k: k["feature_name"])
                    == sorted(other.feature_fit, key=lambda k: k["feature_name"])
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
        return iter(self.feature_fit)

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
