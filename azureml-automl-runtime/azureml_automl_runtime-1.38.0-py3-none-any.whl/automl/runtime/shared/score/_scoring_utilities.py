# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
import logging
from typing import Any, Callable, cast, Dict, Optional, Tuple, Type, Iterable, Union
import numpy as np
import sklearn.preprocessing
import sklearn.metrics
from sklearn.base import TransformerMixin

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import MetricExtrasConstants
from azureml.automl.core.shared.constants import Metric as metric_constants
from azureml.automl.core.shared.exceptions import DataErrorException, ResourceException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.score import _classification, _regression, _forecasting, constants
from azureml.automl.runtime.shared.score._metric_base import Metric


module_logger = logging.getLogger(__name__)


def pad_predictions(y_pred_probs: np.ndarray,
                    train_labels: Optional[np.ndarray],
                    class_labels: Optional[np.ndarray]) -> np.ndarray:
    """
    Add padding to the predicted probabilities for missing training classes.

    If the model is not trained on every class from the dataset it will not
    predict those missing classes.
    Here we insert columns of all zeros for those classes on which the model was not trained.
    Effectively, the model predicts these classes with zero probability.

    :param y_pred_probs: Predictions from a classification model
    :param train_labels: The class labels on which the model was trained
    :param class_labels: The class labels from the full dataset
    :return: Padded predicted probabilities
    """
    if train_labels is None or class_labels is None:
        return y_pred_probs

    if len(train_labels) == len(class_labels):
        return y_pred_probs

    Contract.assert_true(np.setdiff1d(train_labels, class_labels).shape[0] == 0,
                         message="All train_labels must exist in class_labels",
                         target="missing_class_labels", log_safe=True)

    try:
        n_samples = y_pred_probs.shape[0]
        n_class_labels = class_labels.shape[0]
        new_y_pred_probs = np.zeros((n_samples, n_class_labels))
        for class_index, class_label in enumerate(class_labels):
            for train_index, train_label in enumerate(train_labels):
                if class_label == train_label:
                    new_y_pred_probs[:, class_index] = y_pred_probs[:, train_index]
                    break
        return new_y_pred_probs
    except MemoryError as e:
        raise ResourceException._with_error(
            AzureMLError.create(
                InsufficientMemory,
                target='pad_predictions',
                reference_code=ReferenceCodes._PAD_PREDICTIONS_MEMORYERROR,
            ), inner_exception=e) from e


def total_variance(counts, means, variances):
    """
    Compute total population variance.

    Computes the variance of a population given the counts, means, and
    variances of several sub-populations.
    This uses the law of total variance:
    `https://en.wikipedia.org/wiki/Law_of_total_variance`
    var(y) = E[var(y|x)] + var(E[y|x])
        y: predicted value
        x: cross-validation index

    var(y|x) = variances
    E[y|x] = means
    E[var(y|x)] = np.sum(counts * variances) / total_count
    var(E[y|x]) = np.sum(counts * (means - total_mean) ** 2) / total_count
    """
    total_count = np.sum(counts)
    total_mean = np.sum(counts * means) / total_count
    unweighted_vars = variances + (means - total_mean) ** 2
    total_var = np.sum(counts * unweighted_vars) / total_count
    return total_var


class LabelEncodingBinarizer(TransformerMixin):
    """
    Wrapper for sklearn binarizer.

    This wrapper can transform floats, strings, and ints.
    By default, sklearn does not support binarizing floats because they are not
    standard label types. AutoML supports float class labels, so this binarizer
    should be used in those cases.
    """

    def __init__(self):
        """Construct a LabelEncodingBinarizer."""
        self._encoder = sklearn.preprocessing.LabelEncoder()
        self._binarizer = sklearn.preprocessing.LabelBinarizer()

    def __repr__(self) -> str:
        return "{}()".format(self.__class__.__name__)

    def fit(self, fit_values: np.ndarray) -> None:
        """
        Fit the LabelEncodingBinarizer to some labels.

        :param fit_values: Values on which to fit the tranformer.
            These can be of type int, string, or float
        """
        self._binarizer.fit(self._encoder.fit_transform(fit_values))

    def transform(self, transform_values: np.ndarray) -> np.ndarray:
        """
        Transform labels with the encoding binarizer.

        :param transform_values: Values to transform to a one-hot encoding.
        :return: One hot encoding of the values.
        """
        return cast(np.ndarray, self._binarizer.transform(self._encoder.transform(transform_values)))

    def fit_transform(self, values: np.ndarray) -> np.ndarray:
        """
        Encode and binarize labels.

        :param values: Values to fit_transform.
        :return: The transformed values.
        """
        encoded = self._encoder.fit_transform(values)
        return cast(np.ndarray, self._binarizer.fit_transform(encoded))


def class_averaged_score(score_func: Callable[..., float],
                         y_test_bin: np.ndarray,
                         y_pred_proba: np.ndarray,
                         class_labels: np.ndarray,
                         test_class_labels: np.ndarray,
                         average: Optional[str],
                         metric_name: str,
                         multilabel: Optional[bool] = False,
                         **kwargs: Any) -> Union[float, Iterable[float]]:
    """
    Calculate class-averaged metrics like AUC_weighted only on classes present in the validation set.

    For the case when a model was trained on more classes than what the validation set contains
    we will only average over those classes present in the validation set.

    Note that this implementation assumes that the y_pred_proba and y_test_bin matrices have padding so that
    there is a column for all classes present in the entire dataset.  Thus, each column should map to
    the class_labels array.

    Example.
    Dataset classes: 0, 1, 2, 3, 4
    Training classes: 0, 1, 2, 3, 4
    Validation classes: 0, 1, 2, 4

    Initial predicted probabilities: (columns ordered by ascending labels)
    [[.25,  .2,  .3,   0, .25],
     [  0, .25,   0, .25,  .5],
     [.33, .33, .34,   0,  .0],
     [  0,  .7,   0,  .3,   0],
     [.25,  .3,   0,  .2, .25]]

    In this example the model was trained on all classes from the dataset, but class 3 was left
    out of the validation set. There is no meaningful interpretation for the score of class 3,
    so the column for label 3 of the predicted probabilities is dropped from the calculation (see below).

    Resulting predicted probabilities:
    [[.25,  .2,  .3, .25],
     [  0, .25,   0,  .5],
     [.33, .33, .34,  .0],
     [  0,  .7,   0,   0],
     [.25,  .3,   0, .25]]

    From this new matrix of predicted probabilities the class-averaged metrics are calculated normally by sklearn.

    :param score_func: sklearn score function that has an api like sklearn.metrics.roc_auc_score
    :param y_test_bin: Test class label indicator matrix of shape (n_test_examples, len(class_labels))
    :param y_pred_proba: Predicted probability matrix from X_test, shape (n_test_examples, len(class_labels))
    :param class_labels: Class labels present the entire dataset.
    :param test_class_labels: Class labels present in the validation set.
    :param average: Averaging strategy (e.g. "micro", "macro", etc.)
    :param metric_name: Name of the metric.
    :param multilabel: Indicate if it is multilabel classification.
    :param kwargs: Extra keyword arguments to be passed into score_func.
    :return: the output of score_func
    """
    n_classes = len(class_labels)
    dropped_classes = []

    # Micro averaging does not perform class level averaging, so handling imbalanced classes is not needed
    if average != "micro" and n_classes > 2:
        # Assert that padding logic worked correctly
        y_test_bin_padded = y_test_bin.shape[1] == n_classes if y_test_bin.ndim == 2 else False
        y_pred_proba_padded = y_pred_proba.shape[1] == n_classes if y_pred_proba.ndim == 2 else False

        msg = "len(class_labels) = {} should correpond to {}'s shape of = {}"
        assert y_test_bin_padded, msg.format(len(class_labels), "y_test_bin", y_test_bin.shape)
        assert y_pred_proba_padded, msg.format(len(class_labels), "y_pred_proba", y_pred_proba.shape)

        if average is not None:  # Do not perform the intersection logic for classwise metrics
            # Intersection logic for only scoring on classes present in test set
            intersection_labels = np.intersect1d(test_class_labels, class_labels)
            intersection_indices = np.array([i for i, val in enumerate(class_labels) if val in intersection_labels])
            dropped_classes = [_class for _class in class_labels if _class not in intersection_labels]
            if len(dropped_classes) > 0:
                dropped_msg_fmt = "For {} classes not found in the validation set were ignored."
                dropped_msg = dropped_msg_fmt.format(metric_name)
                module_logger.info(dropped_msg)

            y_test_bin = y_test_bin[:, intersection_indices]
            y_pred_proba = y_pred_proba[:, intersection_indices]

    if metric_name == constants.NORM_MACRO_RECALL:
        n_classes = y_test_bin.shape[1]
        return score_func(y_test_bin, y_pred_proba, n_classes=n_classes, **kwargs)
    else:
        ''' Proceed with normal metric computation for multiclass, non-classwise and average_precision metrics which
            do not suffer from metric undefined error when there are no positive and negative samples of a class or
            for classwise metrics in binary class problems with use_binary switch on.
        '''
        metric_undefined_safe_metrics = [constants.AVERAGE_PRECISION_MICRO, constants.AVERAGE_PRECISION_MACRO,
                                         constants.AVERAGE_PRECISION_WEIGHTED, constants.AUC_MICRO,
                                         constants.AVERAGE_PRECISION_CLASSWISE]
        if (not multilabel and average is not None) or metric_name in metric_undefined_safe_metrics or \
                y_test_bin.ndim == 1:
            return score_func(y_test_bin, y_pred_proba, average=average, **kwargs)
        else:
            # Identify classes which does not have positive and negative cases and remove those classes.
            # Else this will result in exception Only one class present in y_true.
            # ROC AUC score is not defined in that case.
            one_class_vector = [i for i in range(y_test_bin.shape[1]) if len(np.unique(y_test_bin[:, i])) != 2]
            if len(one_class_vector) > 0:
                y_test_bin = np.delete(y_test_bin, one_class_vector, 1)
                y_pred_proba = np.delete(y_pred_proba, one_class_vector, 1)
                dropped_msg_fmt = "classes with no positive and negative samples were ignored while computing {}."
                dropped_msg = dropped_msg_fmt.format(metric_name)
                module_logger.info(dropped_msg)
                ignored_classes_fmt = "Ignored classes: {}"
                ignored_msg = ignored_classes_fmt.format(one_class_vector)
                module_logger.info(ignored_msg)
            if y_pred_proba.shape[1] > 0:  # ensure atleast one column
                if average is not None:
                    return score_func(y_test_bin, y_pred_proba, average=average, **kwargs)
                else:
                    classwise_roc = score_func(y_test_bin, y_pred_proba, average=average, **kwargs)
                    # For classwise metrics, introduce np.nan for the classes that are in one_class_vector
                    # as auc is not defined for a single class
                    if len(one_class_vector) > 0:
                        for index in one_class_vector:
                            classwise_roc = np.insert(classwise_roc, index, np.nan)
                    return classwise_roc
            else:
                dropped_msg_fmt = "No classes qualified for {} computation. Returning np.nan."
                dropped_msg = dropped_msg_fmt.format(metric_name)
                module_logger.info(dropped_msg)
                return float(np.nan)


def get_metric_class(metric_name):
    """
    Return the metric class based on the constant name of the metric.

    :param metric: the constant name of the metric
    :return: the class of the metric
    """
    classification_classes = {
        constants.ACCURACY: _classification.Accuracy,
        constants.WEIGHTED_ACCURACY: _classification.WeightedAccuracy,
        constants.BALANCED_ACCURACY: _classification.BalancedAccuracy,
        constants.NORM_MACRO_RECALL: _classification.NormMacroRecall,
        constants.LOG_LOSS: _classification.LogLoss,
        constants.AUC_BINARY: _classification.AUCBinary,
        constants.AUC_MACRO: _classification.AUCMacro,
        constants.AUC_MICRO: _classification.AUCMicro,
        constants.AUC_WEIGHTED: _classification.AUCWeighted,
        constants.AVERAGE_PRECISION_BINARY: _classification.AveragePrecisionBinary,
        constants.AVERAGE_PRECISION_MACRO: _classification.AveragePrecisionMacro,
        constants.AVERAGE_PRECISION_MICRO: _classification.AveragePrecisionMicro,
        constants.AVERAGE_PRECISION_WEIGHTED: _classification.AveragePrecisionWeighted,
        constants.MATTHEWS_CORRELATION: _classification.MatthewsCorrelation,
        constants.F1_BINARY: _classification.F1Binary,
        constants.F1_MACRO: _classification.F1Macro,
        constants.F1_MICRO: _classification.F1Micro,
        constants.F1_WEIGHTED: _classification.F1Weighted,
        constants.PRECISION_BINARY: _classification.PrecisionBinary,
        constants.PRECISION_MACRO: _classification.PrecisionMacro,
        constants.PRECISION_MICRO: _classification.PrecisionMicro,
        constants.PRECISION_WEIGHTED: _classification.PrecisionWeighted,
        constants.RECALL_BINARY: _classification.RecallBinary,
        constants.RECALL_MACRO: _classification.RecallMacro,
        constants.RECALL_MICRO: _classification.RecallMicro,
        constants.RECALL_WEIGHTED: _classification.RecallWeighted,
        constants.ACCURACY_TABLE: _classification.AccuracyTable,
        constants.CONFUSION_MATRIX: _classification.ConfusionMatrix,
        constants.CLASSIFICATION_REPORT: _classification.ClassificationReport,
        constants.IOU: _classification.IOUSamples,
        constants.IOU_MICRO: _classification.IOUMicro,
        constants.IOU_MACRO: _classification.IOUMacro,
        constants.IOU_WEIGHTED: _classification.IOUWeighted,
        constants.PRECISION_CLASSWISE: _classification.PrecisionClasswise,
        constants.RECALL_CLASSWISE: _classification.RecallClasswise,
        constants.F1_CLASSWISE: _classification.F1Classwise,
        constants.IOU_CLASSWISE: _classification.IOUClasswise,
        constants.AUC_CLASSWISE: _classification.AUCClasswise,
        constants.AVERAGE_PRECISION_CLASSWISE: _classification.AveragePrecisionClasswise,
    }      # type: Dict[str, Type[Metric]]
    regression_classes = {
        constants.EXPLAINED_VARIANCE: _regression.ExplainedVariance,
        constants.R2_SCORE: _regression.R2,
        constants.SPEARMAN: _regression.Spearman,
        constants.RMSLE: _regression.RMSLE,
        constants.NORM_RMSLE: _regression.NormRMSLE,
        constants.RMSE: _regression.RMSE,
        constants.NORM_RMSE: _regression.NormRMSE,
        constants.MEAN_ABS_ERROR: _regression.MeanAbsoluteError,
        constants.NORM_MEAN_ABS_ERROR: _regression.NormMeanAbsoluteError,
        constants.MEDIAN_ABS_ERROR: _regression.MedianAbsoluteError,
        constants.NORM_MEDIAN_ABS_ERROR: _regression.NormMedianAbsoluteError,
        constants.MAPE: _regression.MAPE,
        constants.RESIDUALS: _regression.Residuals,
        constants.PREDICTED_TRUE: _regression.PredictedTrue
    }      # type: Dict[str, Type[Metric]]
    forecasting_classes = {
        constants.FORECASTING_RESIDUALS: _forecasting.ForecastResiduals,
        constants.FORECASTING_MAPE: _forecasting.ForecastMAPE,
        constants.FORECASTING_VALIDATE_TABLE: _forecasting.ForecastValidateTable,
        constants.FORECASTING_TRAIN_TABLE: _forecasting.ForecastTrainTable
    }      # type: Dict[str, Type[Metric]]
    class_map = dict()      # type: Dict[str, Type[Metric]]
    class_map.update(classification_classes)
    class_map.update(regression_classes)
    class_map.update(forecasting_classes)

    if metric_name not in class_map:
        raise DataErrorException(
            "Metric class {} was not found in Metric.get_metric_class.".format(metric_name),
            target="metric_name", reference_code="_scoring_utilities.get_metric_class",
            has_pii=True).with_generic_msg("Metric class was not found in Metric.get_metric_class.")
    return class_map[metric_name]


def make_json_safe(o: Any) -> Any:
    """
    Convert a value into something that is safe to parse into JSON.

    :param o: Object to make JSON safe.
    :return: New object
    """
    scalar_types = [int, float, str, type(None)]
    if type(o) in scalar_types:
        return o
    elif isinstance(o, dict):
        return {k: make_json_safe(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [make_json_safe(v) for v in o]
    elif isinstance(o, tuple):
        return tuple(make_json_safe(v) for v in o)
    elif isinstance(o, np.ndarray):
        return make_json_safe(o.tolist())
    else:
        # If item is a numpy scalar type try to convert it to python builtin
        try:
            return o.item()
        except Exception:
            raise DataErrorException(
                "Cannot encode type {}".format(type(o)),
                target="metric_name", reference_code="_scoring_utilities.make_json_safe",
                has_pii=False)


def classification_label_decode(y_transformer: Optional[TransformerMixin],
                                y_test: np.ndarray,
                                y_pred: np.ndarray,
                                class_labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Decode classification labels if a y_transformer is passed.

    This is important for non-scalar metrics, which require the actual labels so that charts
    can be displayed with the correct user-provided labels.

    :param y_transformer: sklearn LabelEncoder transformer
    :param y_test: Actual targets.
    :param y_pred: Predicted targets.
    :param class_labels: All classes found in the full dataset.
    :return: The labels that have been decoded as a tuple.
    """
    if y_transformer is None:
        return y_test, y_pred, class_labels

    y_test_original = y_transformer.inverse_transform(y_test)
    y_pred_original = y_transformer.inverse_transform(y_pred)
    class_labels_original = y_transformer.inverse_transform(class_labels)
    return y_test_original, y_pred_original, class_labels_original


def classification_label_encode(y_test: np.ndarray,
                                y_pred: np.ndarray,
                                class_labels: np.ndarray,
                                positive_label: Optional[Any] = None) -> Tuple[np.ndarray, np.ndarray,
                                                                               np.ndarray, Optional[int]]:
    """
    Encode classification labels that are strings, floats, or negative integers.

    This allows sklearn to operate on integer labels which is the most common format.
    :param y_test: Actual targets.
    :param y_pred: Predicted targets.
    :param class_labels: All classes found in the full dataset.
    :param positive_label: The class treated as positive class for binary classification metrics
    :return: The labels that have been encoded as a tuple.
    """
    metrics_transformer = sklearn.preprocessing.LabelEncoder()
    metrics_transformer.fit(class_labels)
    y_test_encoded = metrics_transformer.transform(y_test)
    y_pred_encoded = metrics_transformer.transform(y_pred)
    class_labels_encoded = metrics_transformer.transform(class_labels)
    if positive_label in class_labels:
        positive_label_encoded = metrics_transformer.transform([positive_label])[0]
    else:
        positive_label_encoded = None
    return y_test_encoded, y_pred_encoded, class_labels_encoded, positive_label_encoded


def get_safe_metric_name(
    metric_name: str,
    mask: str = '[user_metric]'
) -> str:
    """
    Convert a metric name into a string that can be logged.

    :param metric_name: Actual metric name.
    :param mask: String used to mask a PII metric name.
    :return: String that is either the metric name or a masked indicator.
    """
    return metric_name if metric_name in constants.FULL_SET else mask


class ClassificationDataDto:
    """Data transfer object for cleaned classification scoring data.

    :param y_test: Actual targets.
    :param y_pred_probs: The predicted probabilities for all classes.
    :param class_labels: All classes found in the full dataset.
    :param train_labels: Classes as seen (trained on) by the trained model.
    :param sample_weight: Weights for the samples.
    :param y_transformer: Used to inverse transform labels.
    :param multilabel: Indicate if it is multilabel classification.
    :param positive_label: The class treated as positive class for binary classification metrics
    """

    def __init__(
        self,
        y_test: np.ndarray,
        y_pred_probs: np.ndarray,
        class_labels: np.ndarray,
        train_labels: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        y_transformer: Optional[TransformerMixin] = None,
        multilabel: Optional[bool] = False,
        positive_label: Optional[Any] = None
    ):
        # Sort the class labels
        # This is required for both binarization of targets
        # and for matching the columns of predictions
        class_labels = np.unique(class_labels)

        # Some metrics use an eps of 1e-15 by default, which results in nans for float32.
        if y_pred_probs.dtype == np.float32:
            y_pred_probs = y_pred_probs.astype(np.float64)

        # Pad the predictions with 0 columns in case the model wasn't fit on the entire set of class labels
        y_pred_probs_padded = pad_predictions(y_pred_probs, train_labels, class_labels)

        if not multilabel:

            # Choose the class with the highest probability to be the predicted class
            # We can use class_labels here because we have already padded
            y_pred = class_labels[np.argmax(y_pred_probs_padded, axis=1)]

            # Non-scalar metrics operate on the actual class labels
            # If a transformer was passed, use it to get the original labels
            y_test_original, y_pred_original, class_labels_original = classification_label_decode(
                y_transformer, y_test, y_pred, class_labels)

            # Label encode all labels so sklearn classification metrics work
            y_test_encoded, y_pred_encoded, class_labels_encoded, positive_label_encoded = classification_label_encode(
                y_test_original, y_pred_original, class_labels_original, positive_label)

            if positive_label is None:
                if y_pred_probs.shape[1] == 2:
                    positive_label_encoded = 1
                    module_logger.info("No positive_label provided but detected a binary classification task")
                else:
                    module_logger.info("No positive_label provided. Binary classification metrics will return nan")
            else:
                if positive_label_encoded is not None:
                    module_logger.info("positive_label found and binary classification metrics will be calculated")
                else:
                    message = "Cannot find positive_label in class_labels. "
                    message += "Binary classification metrics will return nan.\n"
                    message += "This might happen when using TabularDataset class to prepare your data."
                    module_logger.warning(message)

            encoding_binarizer = LabelEncodingBinarizer()
            encoding_binarizer.fit(class_labels)
            y_test_bin = encoding_binarizer.transform(y_test)

            # Augment the binarized labels for binary classification
            # This is necessary because the binarizer drops one column if there are two labels
            if y_test_bin.shape[1] == 1:
                y_test_bin = np.concatenate((1 - y_test_bin, y_test_bin), axis=1)

            self.y_test_encoded = y_test_encoded
            self.y_test_bin = y_test_bin
            self.y_pred_encoded = y_pred_encoded
            self.y_pred_probs_padded = y_pred_probs_padded
            self.class_labels_encoded = class_labels_encoded
            self.positive_label_encoded = positive_label_encoded
            self.y_test_original = y_test_original
            self.y_pred_original = y_pred_original
            self.class_labels_original = class_labels_original

        else:

            self.y_pred_probs_padded = y_pred_probs_padded
            # multilabel can produce more than one prediction.
            self.y_pred_encoded = (self.y_pred_probs_padded > constants.MULTILABEL_PREDICTION_THRESHOLD).astype(float)
            # y_test values for multilabel is already in one hot encoded format. Label encoding is not applicable.
            # Hence y_test_bin and y_test_encoded are same as y_test.
            self.y_test_encoded = y_test
            self.y_test_bin = y_test
            # original values are not used multilabel classification.
            # Hence original variables are same as encoded variables.
            self.y_test_original = y_test
            self.y_pred_original = self.y_pred_encoded
            y_transformer = cast(TransformerMixin, y_transformer)
            self.class_labels_original = np.array(y_transformer.classes_)
            # one hot encoded format is not applicable for class labels of multilabel.
            self.class_labels_encoded = self.class_labels_original
            # in multilabel setting, there should be no binary metrics
            self.positive_label_encoded = None

        self.positive_label_original = positive_label if self.positive_label_encoded is not None else None

    def get_targets(self, encoded: Optional[bool] = True,
                    classwise: Optional[bool] = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Union[int, None]]:
        if encoded:
            return self.y_test_encoded, self.y_pred_encoded, self.class_labels_encoded, self.positive_label_encoded
        elif classwise:
            return self.y_test_encoded, self.y_pred_encoded, self.class_labels_original, None
        else:
            return self.y_test_original, self.y_pred_original, self.class_labels_original, self.positive_label_original


_table_metrics = set([MetricExtrasConstants.MetricExtrasFormat.format(m)
                     for m in metric_constants.SCALAR_FULL_SET])


def is_table_metric(name: str) -> bool:
    """
    Check by name if a metric is a table metric.

    :param name: The name of the metric.
    :return: True if the metric is a table metric, otherwise False.
    """
    return name in _table_metrics


def log_invalid_score(score: float, metric_name: str) -> None:
    """
    Log a message indicating how the metric score was invalid.

    :param score: The score of the metric.
    :param metric_name: The name of the metric to log.
    """
    if np.isnan(score) or np.isinf(score):
        module_logger.warning("Metric {} had an invalid score ({})".format(metric_name, score))


def clip_score(
    score: float,
    minimum: float,
    maximum: float,
    metric_name: str
) -> float:
    """
    Clip a metric score within a range and log when the score needed to be clipped.

    :param score: The score to clip.
    :param minimum: The minimum in the range to clip.
    :param maximum: The maximum in the range to clip.
    """
    clipped = cast(float, np.clip(score, minimum, maximum))
    if score < minimum or score > maximum:
        module_logger.warning("Metric {} had an invalid score ({}). Clipping to {}".format(
            metric_name, score, clipped))
    return clipped


def _get_debug_stats(y_test: np.ndarray, y_pred: np.ndarray,
                     class_labels: np.ndarray, y_pred_proba: np.ndarray,
                     sample_weight: Optional[np.ndarray] = None) -> Dict[str, Any]:
    y_type, _, _ = sklearn.metrics._classification._check_targets(y_test, y_pred)
    y_test_in_labels = sum(1 if val in class_labels else 0 for val in y_test)
    return {
        'y_true_type': str(y_test.dtype),
        'y_pred_type': str(y_pred.dtype),
        'labels_type': str(class_labels.dtype),
        'y_type': y_type,
        'y_test_in_labels': "{} / {}".format(y_test_in_labels, y_test.shape[0]),
        'proba_type': str(y_pred_proba.dtype),
        'y_true_kind': y_test.dtype.kind,
        'y_pred_kind': y_pred.dtype.kind,
        'labels_kind': class_labels.dtype.kind,
        'proba_kind': y_pred_proba.dtype.kind,
        'y_true_shape': y_test.shape,
        'y_pred_shape': y_pred.shape,
        'labels_shape': class_labels.shape,
        'proba_shape': y_pred_proba.shape,
        'sample_weight_passed': sample_weight is not None,
    }
