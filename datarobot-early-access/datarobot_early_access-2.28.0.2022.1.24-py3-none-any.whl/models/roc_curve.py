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
import numpy as np
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2


class RocCurveThresholdMixin(object):
    roc_points = None

    @staticmethod
    def _validate_threshold(threshold):
        if threshold > 1 or threshold < 0:
            raise ValueError("threshold must be from [0, 1] interval")

    def estimate_threshold(self, threshold):
        """ Return metrics estimation for given threshold.

        Parameters
        ----------
        threshold : float from [0, 1] interval
            Threshold we want estimation for

        Returns
        -------
        dict
            Dictionary of estimated metrics in form of {metric_name: metric_value}.
            Metrics are 'accuracy', 'f1_score', 'false_negative_score', 'true_negative_score',
            'true_negative_rate', 'matthews_correlation_coefficient', 'true_positive_score',
            'positive_predictive_value', 'false_positive_score', 'false_positive_rate',
            'negative_predictive_value', 'true_positive_rate'.

        Raises
        ------
        ValueError
            Given threshold isn't from [0, 1] interval
        """
        self._validate_threshold(threshold)
        for roc_point in self.roc_points:
            if np.isclose(roc_point["threshold"], threshold):
                estimated_roc_point = roc_point
                break
        else:
            # if no exact match - pick closest ROC point with bigger threshold
            roc_points_with_bigger_threshold = [
                roc_point for roc_point in self.roc_points if roc_point["threshold"] > threshold
            ]
            estimated_roc_point = sorted(
                roc_points_with_bigger_threshold, key=lambda rp: rp["threshold"]
            )[0]
        return estimated_roc_point

    def get_best_f1_threshold(self):
        """ Return value of threshold that corresponds to max F1 score.
        This is threshold that will be preselected in DataRobot when you open "ROC curve" tab.

        Returns
        -------
        float
            Threhold with best F1 score.
        """
        roc_point_with_best_f1 = max(self.roc_points, key=lambda roc_point: roc_point["f1_score"])
        return roc_point_with_best_f1["threshold"]


RocPointsTrafaret = t.Dict(
    {
        t.Key("negative_class_predictions"): t.List(t.Float),
        t.Key("positive_class_predictions"): t.List(t.Float),
        t.Key("roc_points"): t.List(
            t.Dict(
                {
                    t.Key("accuracy"): t.Float,
                    t.Key("f1_score"): t.Float,
                    t.Key("false_negative_score"): Int,
                    t.Key("true_negative_score"): Int,
                    t.Key("true_positive_score"): Int,
                    t.Key("false_positive_score"): Int,
                    t.Key("true_negative_rate"): t.Float,
                    t.Key("false_positive_rate"): t.Float,
                    t.Key("true_positive_rate"): t.Float,
                    t.Key("matthews_correlation_coefficient"): t.Float,
                    t.Key("positive_predictive_value"): t.Float,
                    t.Key("negative_predictive_value"): t.Float,
                    t.Key("threshold"): t.Float,
                    t.Key("fraction_predicted_as_positive"): t.Float,
                    t.Key("fraction_predicted_as_negative"): t.Float,
                    t.Key("lift_positive"): t.Float,
                    t.Key("lift_negative"): t.Float,
                }
            ).ignore_extra("*")
        ),
    }
)

RocCurveTrafaret = (
    t.Dict({t.Key("source"): String, t.Key("source_model_id"): String})
    .merge(RocPointsTrafaret)
    .ignore_extra("*")
)


class RocCurve(APIObject, RocCurveThresholdMixin):
    """ ROC curve data for model.

    Attributes
    ----------
    source : str
        ROC curve data source. Can be 'validation', 'crossValidation' or 'holdout'.
    roc_points : list of dict
        List of precalculated metrics associated with thresholds for ROC curve.
    negative_class_predictions : list of float
        List of predictions from example for negative class
    positive_class_predictions : list of float
        List of predictions from example for positive class
    source_model_id : str
        ID of the model this ROC curve represents; in some cases,
        insights from the parent of a frozen model may be used
    """

    _converter = RocCurveTrafaret

    def __init__(
        self,
        source,
        roc_points,
        negative_class_predictions,
        positive_class_predictions,
        source_model_id,
    ):
        self.source = source
        self.roc_points = roc_points
        self.negative_class_predictions = negative_class_predictions
        self.positive_class_predictions = positive_class_predictions
        self.source_model_id = source_model_id

    def __repr__(self):
        return encode_utf8_if_py2(u"RocCurve({})".format(self.source))


class LabelwiseRocCurve(RocCurve):
    """ Labelwise ROC curve data for one label and one source.

    Attributes
    ----------
    source : str
        ROC curve data source. Can be 'validation', 'crossValidation' or 'holdout'.
    roc_points : list of dict
        List of precalculated metrics associated with thresholds for ROC curve.
    negative_class_predictions : list of float
        List of predictions from example for negative class
    positive_class_predictions : list of float
        List of predictions from example for positive class
    source_model_id : str
        ID of the model this ROC curve represents; in some cases,
        insights from the parent of a frozen model may be used
    label : str
        Label name for
    kolmogorov_smirnov_metric : float
        Kolmogorov-Smirnov metric value for label
    auc : float
        AUC metric value for label
    """

    _converter = (
        t.Dict(
            {
                t.Key("label"): String,
                t.Key("kolmogorov_smirnov_metric"): t.Float,
                t.Key("auc"): t.Float,
            }
        )
        .merge(RocCurveTrafaret)
        .ignore_extra("*")
    )

    def __init__(
        self,
        source,
        roc_points,
        negative_class_predictions,
        positive_class_predictions,
        source_model_id,
        label,
        kolmogorov_smirnov_metric,
        auc,
    ):
        super(LabelwiseRocCurve, self).__init__(
            source=source,
            roc_points=roc_points,
            negative_class_predictions=negative_class_predictions,
            positive_class_predictions=positive_class_predictions,
            source_model_id=source_model_id,
        )
        self.label = label
        self.kolmogorov_smirnov_metric = kolmogorov_smirnov_metric
        self.auc = auc
