import numpy as np
import pytest

from azureml.automl.core.shared import constants
from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters
from azureml.automl.dnn.nlp.classification.multiclass.utils import (
    compute_metrics,
    concat_text_columns,
    get_max_seq_length
)


class TestTextClassificationUtils:
    """Tests for utility functions for multi-class text classification."""
    @pytest.mark.parametrize('class_labels, train_labels',
                             [pytest.param(np.array(['ABC', 'DEF', 'XYZ']), np.array(['ABC', 'DEF'])),
                              pytest.param(np.array(['ABC', 'DEF', 'XYZ']), np.array(['ABC', 'DEF', 'XYZ']))])
    def test_compute_metrics(self, class_labels, train_labels):
        predictions = np.random.rand(5, len(train_labels))
        y_val = np.random.choice(class_labels, size=5)
        results = compute_metrics(y_val, predictions, class_labels, train_labels)
        metrics_names = list(constants.Metric.CLASSIFICATION_SET)
        assert all(key in metrics_names for key in results)

    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_concat_text_columns(self, MulticlassDatasetTester, include_label_col):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col" if include_label_col else None
        all_text_cols = [column for column in input_df.columns
                         if label_column_name is None or label_column_name != column]
        expected_concatenated_text = input_df[all_text_cols].apply(lambda x: ". ".join(x.values.astype(str)), axis=1)
        for index in range(len(input_df)):
            concatenated_text = concat_text_columns(input_df.iloc[index], input_df.columns, label_column_name)
            assert concatenated_text == expected_concatenated_text[index]

    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.usefixtures('MulticlassTokenizer')
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True])
    @pytest.mark.parametrize('is_long_range_text', [True, False])
    def test_get_max_seq_length(self, MulticlassDatasetTester, is_long_range_text, MulticlassTokenizer):
        input_df = MulticlassDatasetTester.get_data(is_long_range_text).copy()
        label_column_name = "labels_col"
        max_seq_length = get_max_seq_length(input_df, MulticlassTokenizer, label_column_name)
        if is_long_range_text:
            assert max_seq_length == MultiClassParameters.MAX_SEQ_LENGTH_256
        else:
            assert max_seq_length == MultiClassParameters.MAX_SEQ_LENGTH_128
