import unittest
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper

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
            'ids': torch.tensor(self.inputs['input_ids'], dtype=torch.long),
            'mask': torch.tensor(self.inputs['attention_mask'], dtype=torch.long),
            'token_type_ids': torch.tensor(self.inputs['token_type_ids'], dtype=torch.long),
            'targets': torch.randint(self.num_labels, (2,)).float()
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
def test_transform_1():
    text_dataset = MockTextDataset(5, 2)
    model = MockModel(2)
    wrapper = ModelWrapper(model, "some_tokenizer", "some_language", "some_vectorizer", "some_column")
    output = wrapper.transform(text_dataset, batch_size=1)

    assert model.n_forward_called == 5, "inference was not run for all rows of dataset"
    assert len(output) == 5


@unittest.skipIf(not has_torch, "torch not installed")
def test_transform_batched():
    text_dataset = MockTextDataset(6, 2)
    model = MockModel(2)
    wrapper = ModelWrapper(model, "some_tokenizer", "some_language", "some_vectorizer", "some_column")
    output = wrapper.transform(text_dataset, batch_size=2)

    assert model.n_forward_called == 3, "inference was not batched correctly"
    assert len(output) == 6


@unittest.skipIf(not has_torch, "torch not installed")
def test_predict():

    data = pd.DataFrame({"text": ["some data input"]})
    model = MockModel(2)
    vectorizer = CountVectorizer()
    vectorizer.fit(["label0", "label1", "label2"])
    wrapper = ModelWrapper(model, "some_tokenizer", "some_language", vectorizer, "some_column")
    output = wrapper.predict(data, batch_size=3)
    assert len(output) == 1
