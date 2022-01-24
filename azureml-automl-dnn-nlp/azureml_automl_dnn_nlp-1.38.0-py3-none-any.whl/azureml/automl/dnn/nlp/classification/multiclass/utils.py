# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions for multi-class classification."""

import logging
import numpy as np
import os
import pandas as pd
import scipy
from transformers import AutoTokenizer
from typing import Any, Dict, Optional, Union

from azureml.automl.core.shared import constants
from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters, MultiClassInferenceLiterals
from azureml.automl.dnn.nlp.common.constants import OutputLiterals
from azureml.automl.runtime._ml_engine import evaluate_classifier

_logger = logging.getLogger(__name__)


def compute_metrics(y_val: np.ndarray, predictions: np.ndarray, class_labels: np.ndarray,
                    train_labels: np.ndarray) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Function to compute metrics like accuracy and auc-weighted

    :param predictions: Predictions on the validation/test dataset used for computing metrics.
    :return: A dictionary mapping metric name to metric score.
    """
    probas = scipy.special.softmax(predictions, axis=1)
    metrics_names = list(constants.Metric.CLASSIFICATION_SET)
    return evaluate_classifier(y_val, probas, metrics_names, class_labels, train_labels)


def concat_text_columns(row: pd.Series, df_columns: pd.Index, label_column_name: Optional[str]) -> str:
    """Concatenate all text columns

    :param row: One row from the dataframe represented as a column-like series with column names now as indices
    :param label_column_name: Name/title of the label column
    :return: concatenated text data from a row of the dataframe
    """
    cols_to_exclude = [label_column_name] if label_column_name is not None\
        and label_column_name in df_columns else []
    return row.drop(index=cols_to_exclude).astype(str).str.cat(sep=". ")


def get_max_seq_length(train_df: pd.DataFrame, tokenizer: AutoTokenizer, label_column_name: str) -> int:
    """
    Heuristic to determine optimal max_seq_length parameter.
    If the fraction of training examples with length of the text document exceeding 128 tokens/words
    is greater than an empirically determined threshold, then use a higher value for max_seq_length.
    Currently it gets set to 256 rather than 128 if the aforementioned condition is satisfied.

    :param train_df: training data to be leveraged for computing max_seq_length
    :param tokenizer: tokenizer to be used to tokenize the data
    :param label_column_name: Name/title of the label column
    :return: dynamically computed max sequence length
    """
    text_len = []
    for _, row in train_df.iterrows():
        concatenated_text_from_train_sample = concat_text_columns(row, train_df.columns, label_column_name)
        tokenized = tokenizer.tokenize(concatenated_text_from_train_sample)
        text_len.append(len(tokenized))

    frac_longer_than_128 = sum(i > 128 for i in text_len) / len(text_len)
    frac_longer_than_256 = sum(i > 256 for i in text_len) / len(text_len)
    _logger.info("Dataset Stats: Mean length of text={}\nMax length of text={}\nMedian length of text={}\n\
        Fraction of number of rows with len of text longer than 128 tokens={}\n\
        Fraction of number of rows with len of text longer than 256 tokens={}".format(
        np.mean(text_len), np.max(text_len), np.median(text_len), frac_longer_than_128, frac_longer_than_256))

    if frac_longer_than_128 >= MultiClassParameters.MAX_SEQ_LENGTH_THRESHOLD:
        max_seq_length = MultiClassParameters.MAX_SEQ_LENGTH_256
    else:
        max_seq_length = MultiClassParameters.MAX_SEQ_LENGTH_128

    if not os.path.exists(OutputLiterals.OUTPUT_DIR):
        os.mkdir(OutputLiterals.OUTPUT_DIR)
    np.save(OutputLiterals.OUTPUT_DIR + '/' + MultiClassInferenceLiterals.MAX_SEQ_LENGTH, max_seq_length)

    return max_seq_length
