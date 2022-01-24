# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classification metrics for the package."""

from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.runtime.shared.score.scoring import constants
from .automl_classification_metrics import AutoMLClassificationMetrics
from ..classification.common import constants as classification_constants
from ..common.logging_utils import get_logger

logger = get_logger(__name__)


class ClassificationMetrics:
    """Class to calculate classification metrics.

    This class is modeled on the ignite Metrics class.
    Allows us to aggregate metrics per batch and
    compute them only at the end of every epoch.
    """

    def __init__(self, labels, multilabel=False):
        """
        :param labels: class labels
        :type labels: List of class labels
        :param multilabel: flag indicating whether this is multilabel problem
        :type multilabel: bool
        """
        self.labels = labels
        self._multilabel = multilabel
        self._unsupported_metrics = set([])

        self._automl_classification_metrics = {
            MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS:
                AutoMLClassificationMetrics(self.labels, self._multilabel,
                                            is_train=False),
            MetricsLiterals.AUTOML_CLASSIFICATION_TRAIN_METRICS:
                AutoMLClassificationMetrics(self.labels, self._multilabel,
                                            is_train=True)
        }

        if not multilabel:
            self._unsupported_metrics.add(constants.IOU)
            self._unsupported_metrics.add(constants.IOU_MICRO)
            self._unsupported_metrics.add(constants.IOU_MACRO)
            self._unsupported_metrics.add(constants.IOU_WEIGHTED)
            self._unsupported_metrics.add(constants.IOU_CLASSWISE)
        else:
            self._unsupported_metrics.add(constants.ACCURACY_TABLE)
            self._unsupported_metrics.add(constants.CONFUSION_MATRIX)
            if len(self.labels) < 2:
                self._unsupported_metrics.add(constants.ACCURACY)

        # Below automl metrics are not supported for classification
        for metric in classification_constants.UNSUPPORTED_CLASSIFICATION_METRICS:
            self._unsupported_metrics.add(metric)

    def metric_supported(self, metric):
        """ Check if a metric is supported.

        :param metric: Name of the metric.
        :type metric: MetricsLiterals
        :return: Boolean indicating whether a metric is supported.
        """
        return metric not in self._unsupported_metrics

    def reset(self, is_train=False):
        """Resets metric."""

        if is_train:
            self._automl_classification_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_TRAIN_METRICS].reset()
        else:
            self._automl_classification_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS].reset()

    def update(self, probs=None, labels=None, is_train=False):
        """Update the metrics.

        :param probs: probabilities
        :type probs: torch.Tensor
        :param labels: labels
        :type labels: torch.Tensor
        :param is_train: flag indicating if it is training or validation run
        :type is_train: bool
        """
        if is_train:
            train_metrics = self._automl_classification_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_TRAIN_METRICS]
            train_metrics.update((probs, labels))
        else:
            eval_metrics = self._automl_classification_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS]
            eval_metrics.update((probs, labels))

    def compute(self, is_train=False):
        """Compute the metrics."""

        metrics = {}

        if is_train:
            metrics[MetricsLiterals.AUTOML_CLASSIFICATION_TRAIN_METRICS] = \
                self._automl_classification_metrics[
                    MetricsLiterals.AUTOML_CLASSIFICATION_TRAIN_METRICS].compute()
        else:
            metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS] = \
                self._automl_classification_metrics[
                    MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS].compute()

        return metrics
