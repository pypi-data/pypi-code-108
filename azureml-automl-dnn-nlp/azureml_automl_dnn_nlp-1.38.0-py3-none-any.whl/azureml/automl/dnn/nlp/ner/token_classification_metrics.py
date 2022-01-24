# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Named entity recognition metrics class."""
import logging
import numpy as np
import scipy
from seqeval.metrics import accuracy_score
from seqeval.metrics.sequence_labeling import precision_recall_fscore_support
from typing import Dict, List, Tuple

from torch import nn
from transformers import EvalPrediction

from azureml.automl.core.shared.constants import Metric

logger = logging.getLogger(__name__)


class TokenClassificationMetrics:
    """Compute metrics for token classification task"""

    def __init__(self, label_list: List[str]):
        """
        Token classification metrics constructor func.

        :param label_list: unique labels list
        """
        self.label_list = label_list
        self.label_map = {i: label for i, label in enumerate(label_list)}

    def align_predictions_with_proba(
            self,
            predictions: np.ndarray,
            label_ids: np.ndarray
    ) -> Tuple[List[int], List[int], List[int]]:
        """Align the predictions.

        :predictions: array of predictions
        :label_ids: array of label ids
        """
        preds = np.argmax(predictions, axis=2)
        probas = scipy.special.softmax(predictions, axis=2)
        pred_probas = np.amax(probas, axis=2)
        batch_size, seq_len = preds.shape

        out_label_list = [[] for _ in range(batch_size)]
        preds_list = [[] for _ in range(batch_size)]
        preds_proba_list = [[] for _ in range(batch_size)]

        for i in range(batch_size):
            for j in range(seq_len):
                if label_ids[i, j] != nn.CrossEntropyLoss().ignore_index:
                    out_label_list[i].append(self.label_map[label_ids[i][j]])
                    preds_list[i].append(self.label_map[preds[i][j]])
                    preds_proba_list[i].append(pred_probas[i][j])

        return preds_list, out_label_list, preds_proba_list

    def compute_metrics(self, p: EvalPrediction) -> Dict:
        """Compute the metrics.

        :p: EvalPrediction that contains the predictions and the label ids
        """
        # Prepare predictions and true labels to calculate metrics with
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)

        # Remove ignored index (special tokens)
        true_predictions = [
            [self.label_list[pred] for (pred, lbl) in zip(prediction, label) if lbl != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [self.label_list[lbl] for (pred, lbl) in zip(prediction, label) if lbl != -100]
            for prediction, label in zip(predictions, labels)
        ]

        # We are using seqeval to calculate metrics instead of sklearn for other classification problem
        # because seqeval supports evaluation at entity-level
        results = dict()
        # accuracy
        accuracy = accuracy_score(y_true=true_labels, y_pred=true_predictions)
        # micro averages
        precision_micro, recall_micro, f1_micro, _ = precision_recall_fscore_support(
            y_true=true_labels, y_pred=true_predictions, average='micro'
        )
        # macro averages
        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true=true_labels, y_pred=true_predictions, average='macro'
        )
        # weighted averages
        precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_true=true_labels, y_pred=true_predictions, average='weighted'
        )

        # Create result dictionary
        results[Metric.Accuracy] = accuracy
        results[Metric.F1Micro] = f1_micro
        results[Metric.F1Macro] = f1_macro
        results[Metric.F1Weighted] = f1_weighted
        results[Metric.PrecisionMicro] = precision_micro
        results[Metric.PrecisionMacro] = precision_macro
        results[Metric.PrecisionWeighted] = precision_weighted
        results[Metric.RecallMicro] = recall_micro
        results[Metric.RecallMacro] = recall_macro
        results[Metric.RecallWeighted] = recall_weighted

        return results
