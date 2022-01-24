# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utilities for text-classification-multilabel task."""

import numpy as np
from sklearn import metrics
from sklearn.metrics import precision_recall_fscore_support


def compute_threshold_metrics(outputs, targets):
    """
    Function to compute metrics using different thresholds on confidence values

    :param outputs: np.array consisting of confidence values per label
    :param targets: np.array consisting of ground truth labels (one-hot encoded)
    :return: dictionary containing metrics produced using different thresholds
    """

    threshold_values = np.linspace(0, 1, 21)
    threshold_values = threshold_values.round(decimals=2)

    metrics_dict = {
        'threshold': threshold_values,
        'accuracy': [],
        'f1_score_micro': [],
        'f1_score_macro': [],
        'f1_score_weighted': [],
        'recall_micro': [],
        'recall_macro': [],
        'recall_weighted': [],
        'precision_micro': [],
        'precision_macro': [],
        'precision_weighted': [],
        'num_labels': []
    }

    for threshold in threshold_values:
        t_outputs = np.array(outputs) >= threshold
        accuracy = metrics.accuracy_score(targets, t_outputs)
        macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
            targets, t_outputs, average="macro")
        weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
            targets, t_outputs, average="weighted")
        micro_precision, micro_recall, micro_f1, _ = precision_recall_fscore_support(
            targets, t_outputs, average="micro")

        metrics_dict['accuracy'].append(accuracy)
        metrics_dict['f1_score_micro'].append(micro_f1)
        metrics_dict['f1_score_macro'].append(macro_f1)
        metrics_dict['f1_score_weighted'].append(weighted_f1)
        metrics_dict['recall_micro'].append(micro_recall)
        metrics_dict['recall_macro'].append(macro_recall)
        metrics_dict['recall_weighted'].append(weighted_recall)
        metrics_dict['precision_micro'].append(micro_precision)
        metrics_dict['precision_macro'].append(macro_precision)
        metrics_dict['precision_weighted'].append(weighted_precision)
        metrics_dict['num_labels'].append(np.sum(t_outputs))

    return metrics_dict
