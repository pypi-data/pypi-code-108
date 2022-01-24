import pandas as pd
import pytest
from transformers import AutoTokenizer
from azureml.automl.dnn.nlp.common.constants import ModelNames


class MulticlassTestDataset:
    def __init__(self, multiple_text_column, include_label_col, is_val_df=False):
        self.multiple_text_column = multiple_text_column
        self.include_label_col = include_label_col
        self.is_val_df = is_val_df

    def get_data(self, is_long_range_text=False):
        text_col_1 = [
            'This is a small sample dataset containing cleaned text data.',
            'It was created manually so that it can be used for tests in text-classification tasks.',
            'It can be leveraged in tests to verify that codeflows are working as expected.',
            'It can also be used to verify that a machine learning model training successfully.'
        ]
        if is_long_range_text:  # Intentionally making one of the texts really long for higher max-seq-length
            text_col_1.append('It should not be used to validate the multiple text columns performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance'
                              + ' It should not be used to validate the multiple text columns model performance')
        else:
            text_col_1.append('It should not be used to validate the multiple text columns model performance')
        data = {'text_first': text_col_1}

        if self.multiple_text_column:
            text_col_sec = [
                'This is an additional column.',
                'It was created to test the multiple-text columns scenario for classification.',
                'It can be leveraged in tests to verify that multiple-column codeflows are functional.',
                'It can also be used to verify that a ML model trained successfully with multiple columns.',
                'It should not be used to validate the model performance using metrics.']
            data['text_second'] = text_col_sec
        if self.include_label_col:
            if self.is_val_df:
                data['labels_col'] = ["XYZ", "DEF", "ABC", "ABC", "XYZ"]
            else:
                data['labels_col'] = ["XYZ", "PQR", "ABC", "ABC", "XYZ"]

        return pd.DataFrame(data)


@pytest.fixture
def MulticlassDatasetTester(multiple_text_column, include_label_col):
    """Create MulticlassDatasetTester object for training data"""
    return MulticlassTestDataset(multiple_text_column, include_label_col)


@pytest.fixture
def MulticlassValDatasetTester(multiple_text_column, include_label_col):
    """Create MulticlassDatasetTester object for validation data"""
    return MulticlassTestDataset(multiple_text_column, include_label_col, is_val_df=True)


@pytest.fixture
def MulticlassTokenizer():
    """Returns tokenizer for multiclass text classification"""
    return AutoTokenizer.from_pretrained(ModelNames.BERT_BASE_CASED, use_fast=True)
