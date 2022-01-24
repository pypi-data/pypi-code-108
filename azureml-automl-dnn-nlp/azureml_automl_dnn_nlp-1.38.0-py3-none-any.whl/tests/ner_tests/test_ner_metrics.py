import pytest
import unittest

import numpy as np

from azureml.automl.core.shared.constants import Metric
from azureml.automl.dnn.nlp.ner.token_classification_metrics import TokenClassificationMetrics

try:
    from torch import nn
    has_torch = True
except ImportError:
    has_torch = False

try:
    from transformers import EvalPrediction
    has_transformers = True
except ImportError:
    has_transformers = False


@pytest.fixture
def get_preds_and_label_ids():
    label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
    token_classification_metrics = TokenClassificationMetrics(label_list)
    batch_size = 3
    seq_len = 5
    predictions = np.random.rand(batch_size, seq_len, len(label_list))
    label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
    return token_classification_metrics, batch_size, seq_len, predictions, label_ids, label_list


@pytest.mark.usefixtures('new_clean_dir')
class TestTokenClassificationMetrics:
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_align_predictions_with_proba(self, get_preds_and_label_ids):
        token_classification_metrics, batch_size, seq_len, predictions, label_ids, label_list = \
            get_preds_and_label_ids
        preds_list, out_label_list, preds_proba_list = \
            token_classification_metrics.align_predictions_with_proba(predictions, label_ids)
        assert (len(preds_list) == batch_size and len(out_label_list) == batch_size
                and len(preds_proba_list) == batch_size)
        for preds in preds_list:
            assert len(preds) == seq_len
            assert all(item in label_list for item in preds)
        for out_label in out_label_list:
            assert len(out_label) == seq_len
            assert all(item in label_list for item in out_label)
        for preds in preds_proba_list:
            assert len(preds) == seq_len
            assert all(0 <= item < 1 for item in preds)

        label_ids[1][4] = label_ids[2][3] = label_ids[2][4] = nn.CrossEntropyLoss().ignore_index
        preds_list, out_label_list, preds_proba_list = \
            token_classification_metrics.align_predictions_with_proba(predictions, label_ids)
        assert (len(preds_list) == batch_size and len(out_label_list) == batch_size
                and len(preds_proba_list) == batch_size)
        assert len(preds_list[0]) == 5 and len(preds_list[1]) == 4 and len(preds_list[2]) == 3
        assert len(out_label_list[0]) == 5 and len(out_label_list[1]) == 4 and len(out_label_list[2]) == 3
        assert len(preds_proba_list[0]) == 5 and len(preds_proba_list[1]) == 4 and len(preds_proba_list[2]) == 3
        for preds in preds_list:
            assert all(item in label_list for item in preds)
        for out_label in out_label_list:
            assert all(item in label_list for item in out_label)
        for preds in preds_proba_list:
            assert all(item >= 0 and item < 1 for item in preds)

    @unittest.skipIf(not has_torch, "torch not installed")
    @unittest.skipIf(not has_transformers, "transformers not installed")
    def test_compute_metrics(self, get_preds_and_label_ids):
        token_classification_metrics, batch_size, seq_len, predictions, label_ids, label_list = \
            get_preds_and_label_ids
        metrics = token_classification_metrics.compute_metrics(EvalPrediction(predictions, label_ids))
        assert all(0 <= value <= 1 for value in metrics.values())
        assert all(key in metrics for key in Metric.TEXT_NER_PRIMARY_SET)
