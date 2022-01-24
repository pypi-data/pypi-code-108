# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" AutoML classification metrics computation wrapper class."""

import numpy as np
from itertools import chain
from ignite.metrics import EpochMetric
from azureml.automl.runtime.shared.score.scoring import score_classification
from azureml.automl.runtime.shared.score.scoring import constants
from ..classification.common import constants as classification_constants
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MultiLabelBinarizer
from ..common.logging_utils import get_logger

logger = get_logger(__name__)


def _automl_classification_metrics_compute_fn_wrapper(labels, multilabel, is_train):
    """
    This wrapper method will help set the metrics to be computed depending on the flags.

    :param labels: class labels
    :type labels: List of class labels
    :param multilabel: flag indicating whether this is multilabel problem
    :type multilabel: bool
    :param is_train: flag indicating whether the metric is computed with training data or not.
    :type is_train: bool
    :return: Dictionary of (MetricLiteral, metric values).
    """

    def automl_classification_metrics_compute_fn(y_preds, y_targets):

        y_true = y_targets.detach().numpy()
        y_pred = y_preds.detach().numpy()

        metrics_names = list()

        ''' Logic to add dummy labels when there is only single label to overcome automl validation error.
            ~~dummy was chosen as the dummy label to ensure that this label always gets added at the last given its
            ascii value.There is no impact in metrics calculation as there is no support(samples) for the dummy label.
        '''
        if len(labels) == 1:
            labels.append("~~dummy")
            logger.warning("Only primary metrics are defined for single class problem.")
        if y_pred.ndim == 1:
            y_pred = np.expand_dims(y_pred, axis=1)
            y_pred_dummy = np.zeros(y_pred.shape[0])
            y_pred_dummy = np.expand_dims(y_pred_dummy, axis=1)
            y_pred = np.concatenate((y_pred, y_pred_dummy), axis=1)
        if multilabel and y_true.ndim == 1:
            y_true = np.expand_dims(y_true, axis=1)
            y_true_dummy = np.zeros(y_true.shape[0])
            y_true_dummy = np.expand_dims(y_true_dummy, axis=1)
            y_true = np.concatenate((y_true, y_true_dummy), axis=1)

        if not multilabel:
            if constants.ACCURACY not in metrics_names:
                metrics_names.append(constants.ACCURACY)
            y_transformer = LabelEncoder()
            y_transformer.fit(labels)
        else:
            if constants.IOU not in metrics_names:
                metrics_names.append(constants.IOU)
            y_transformer = MultiLabelBinarizer()
            y_transformer.fit([labels])

        if not is_train:
            ''' Add non-primary metrics only when no of classes > 1 as ROC metrics are not relevant
                for one-class classes. Single label classification runs are only applicable for benchmarking.'''
            test_labels = np.array(y_transformer.inverse_transform(y_true))
            test_labels_unique = list()
            if multilabel:
                for item in test_labels:
                    test_labels_unique.extend([*item])
                test_labels_unique = np.unique(np.array(test_labels_unique))
            else:
                test_labels_unique = np.unique(np.array(test_labels))

            if len(test_labels_unique) > 1:
                for metric in chain(constants.CLASSIFICATION_SCALAR_SET, constants.CLASSIFICATION_CLASSWISE_SET,
                                    [constants.CLASSIFICATION_REPORT]):
                    if metric not in chain(classification_constants.UNSUPPORTED_CLASSIFICATION_METRICS,
                                           [constants.IOU_CLASSWISE]):
                        metrics_names.append(metric)

                if not multilabel:
                    metrics_names.append(constants.CONFUSION_MATRIX)
                    metrics_names.append(constants.ACCURACY_TABLE)
                else:
                    metrics_names.extend(constants.CLASSIFICATION_MULTILABEL_SET)
                    metrics_names.append(constants.IOU_CLASSWISE)

        num_classes = len(labels)
        metrics = score_classification(y_true, y_pred, metrics_names,
                                       np.array(range(num_classes)),
                                       np.array(range(num_classes)),
                                       y_transformer=y_transformer,
                                       multilabel=multilabel)

        return metrics

    return automl_classification_metrics_compute_fn


class AutoMLClassificationMetrics(EpochMetric):
    """
    This metric calls the Automated ML Classification Metrics Scoring Module.
    """

    def __init__(self, labels, multilabel=False, is_train=False):
        """
        :param labels: class labels
        :type labels: List of class labels
        :param multilabel: flag indicating whether this is multilabel problem
        :type multilabel: bool
        :param is_train: flag indicating whether the metric is computed with training data or not.
        :type is_train: bool
        """

        super(AutoMLClassificationMetrics, self).__init__(
            _automl_classification_metrics_compute_fn_wrapper(
                labels, multilabel, is_train))
