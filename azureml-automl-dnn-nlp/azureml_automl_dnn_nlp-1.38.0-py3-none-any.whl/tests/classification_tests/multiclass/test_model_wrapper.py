import unittest
from unittest.mock import patch
import pandas as pd
import pytest
from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


class MockTextDataset(torch.utils.data.Dataset):
    def __init__(self, size, num_labels):
        # Inputs created using BertTokenizer('this is a sentence')
        self.inputs = {'input_ids': [101, 2023, 2003, 1037, 6251, 102],
                       'token_type_ids': [0, 0, 0, 0, 0, 0],
                       'attention_mask': [1, 1, 1, 1, 1, 1]}
        self.dataset_size = size
        self.num_labels = num_labels

    def __len__(self):
        return self.dataset_size

    def __getitem__(self, index):
        return {
            'input_ids': torch.tensor(self.inputs['input_ids'], dtype=torch.long),
            'attention_mask': torch.tensor(self.inputs['attention_mask'], dtype=torch.long),
            'token_type_ids': torch.tensor(self.inputs['token_type_ids'], dtype=torch.long),
        }


class MockModel(torch.nn.Module):
    def __init__(self, num_labels):
        super(MockModel, self).__init__()
        self.num_labels = num_labels
        self.n_forward_called = 0

    def forward(self, input_ids, attention_mask, token_type_ids):
        self.n_forward_called = self.n_forward_called + 1
        return torch.rand(input_ids.shape[0], self.num_labels)


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.usefixtures('MulticlassTokenizer')
def test_transform(MulticlassTokenizer):
    text_dataset = MockTextDataset(5, 2)
    model = MockModel(2)
    wrapper = ModelWrapper(model, ["label1", "label2"], MulticlassTokenizer,
                           MultiClassParameters.MAX_SEQ_LENGTH_128)
    output = wrapper.transform(text_dataset)

    assert model.n_forward_called == 1, "inference was not run for all rows of dataset"
    assert len(output) == 5


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.usefixtures('MulticlassTokenizer')
def test_transform_batched(MulticlassTokenizer):
    text_dataset = MockTextDataset(16, 2)
    model = MockModel(2)
    wrapper = ModelWrapper(model, ["label1", "label2"], MulticlassTokenizer,
                           MultiClassParameters.MAX_SEQ_LENGTH_128)
    output = wrapper.transform(text_dataset)

    assert model.n_forward_called == 2, "inference was not batched correctly"
    assert len(output) == 16


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.usefixtures('MulticlassTokenizer')
def test_predict(MulticlassTokenizer):
    data = pd.DataFrame({"text": ["some data input"]})
    model = MockModel(2)
    wrapper = ModelWrapper(model, ["label1", "label2"], MulticlassTokenizer,
                           MultiClassParameters.MAX_SEQ_LENGTH_128)
    datawrapper = "azureml.automl.dnn.nlp.classification.multiclass.model_wrapper.PyTorchMulticlassDatasetWrapper"
    with patch(datawrapper, return_value=MockTextDataset(5, 2)):
        output = wrapper.predict(data)
    assert len(output) == 5
