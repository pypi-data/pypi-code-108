# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model Wrapper class to encapsulate automl model functionality"""

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer, default_data_collator, Trainer

from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from azureml.automl.runtime.featurizer.transformer import AutoMLTransformer


class ModelWrapper(AutoMLTransformer):
    """Class to wrap AutoML NLP models in the AutoMLTransformer interface"""

    def __init__(self,
                 model: torch.nn.Module,
                 train_label_list: list,
                 tokenizer: AutoTokenizer,
                 max_seq_length: int):
        """Transform the input data into outputs tensors from model

        :param trainer: Trained HuggingFace trainer
        :param dataset_language: language for tokenization
        """
        super().__init__()
        self.model = model.to("cpu")
        self.tokenizer = tokenizer
        self.train_label_list = train_label_list
        self.max_seq_length = max_seq_length

    def transform(self,
                  dataset: Dataset):
        """Transform the input data into outputs tensors using model

        :param dataset: Pytorch dataset object which returns items in the format {'ids', 'mask', 'token_type_ids'}
        :return: List of arrays representing outputs
        """

        trainer = Trainer(model=self.model, data_collator=default_data_collator)
        return trainer.predict(test_dataset=dataset).predictions

    def predict(self,
                X: pd.DataFrame):
        """Predict output labels for text datasets

        :param X: pandas dataframe in the same format as training data, without label columns
        :return: list of output labels equal to the size of X
        """
        dataset = PyTorchMulticlassDatasetWrapper(X,
                                                  self.train_label_list,
                                                  self.tokenizer,
                                                  self.max_seq_length,
                                                  label_column_name=None)
        predictions = self.transform(dataset)
        preds = np.argmax(predictions, axis=1)
        predicted_labels = [self.train_label_list[item] for item in preds]
        return predicted_labels
