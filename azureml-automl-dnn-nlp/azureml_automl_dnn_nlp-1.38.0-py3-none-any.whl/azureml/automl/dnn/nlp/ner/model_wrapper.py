# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model Wrapper class to encapsulate automl model functionality"""

import torch
from typing import Optional
from transformers import Trainer, default_data_collator, PreTrainedTokenizer
from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import DatasetWrapper
from azureml.automl.dnn.nlp.ner.token_classification_metrics import TokenClassificationMetrics
from azureml.automl.dnn.nlp.common.constants import DataLiterals, Split
from sklearn.base import BaseEstimator


class ModelWrapper(BaseEstimator):
    """Class to wrap AutoML NLP models in the AutoMLTransformer interface"""

    def __init__(self,
                 model: torch.nn.Module,
                 label_list: list,
                 tokenizer: PreTrainedTokenizer,
                 max_seq_length: Optional[int] = 128):
        """Transform the input data into outputs tensors from model
        :param model: Trained model, preferably trained using HuggingFace trainer
        :param label_list: List of labels that the model was trained on
        :param dataset_language: language for tokenization
        :param tokenizer: PretrainedTokenizer used by the DatasetWrapper while training
        """
        super().__init__()
        self.model = model.to("cpu")
        self.label_list = label_list
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length

    def predict(self,
                X: str):
        """Predict output labels for text datasets
        :param X: String of tokens in CoNLL format, without labels
        :return: String of labeled X, in CoNLL format
        """
        dataset = DatasetWrapper(X,
                                 tokenizer=self.tokenizer,
                                 labels=self.label_list,
                                 max_seq_length=self.max_seq_length,
                                 mode=Split.test)

        trainer = Trainer(model=self.model, data_collator=default_data_collator)
        raw_predictions, label_ids, _ = trainer.predict(test_dataset=dataset)

        token_classification_metrics = TokenClassificationMetrics(self.label_list)
        aligned_predictions, _, _ = token_classification_metrics.align_predictions_with_proba(raw_predictions,
                                                                                              label_ids)

        prediction_strings = []
        for i in range(len(aligned_predictions)):
            words = [item for item in dataset.data[i].split("\n") if item not in DataLiterals.NER_IGNORE_TOKENS]
            preds = aligned_predictions[i]

            sample_str = "\n".join(["{} {}".format(item[0], item[1]) for item in zip(words, preds)])
            prediction_strings.append(sample_str)

        return "\n\n".join(prediction_strings)
