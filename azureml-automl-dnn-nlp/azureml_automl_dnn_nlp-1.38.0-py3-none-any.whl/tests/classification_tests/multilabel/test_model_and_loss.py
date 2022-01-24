import unittest
import pytest
from unittest.mock import patch

from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.dnn.nlp.classification.multilabel.bert_class import BERTClass

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


@pytest.fixture
def get_input_tensors():
    # Inputs created using BertTokenizer('this is a sentence')
    inputs = {'input_ids': [101, 2023, 2003, 1037, 6251, 102],
              'token_type_ids': [0, 0, 0, 0, 0, 0],
              'attention_mask': [1, 1, 1, 1, 1, 1]}

    ids = torch.tensor(inputs['input_ids'], dtype=torch.long).unsqueeze_(0)
    token_type_ids = torch.tensor(inputs['token_type_ids'], dtype=torch.long).unsqueeze_(0)
    attention_mask = torch.tensor(inputs['attention_mask'], dtype=torch.long).unsqueeze_(0)
    return ids, token_type_ids, attention_mask


class MockBertModel(torch.nn.Module):
    def __init__(self):
        super(MockBertModel, self).__init__()
        return

    def forward(self, ids, attention_mask, token_type_ids):
        return None, torch.randn(ids.shape[0], BERTClass.BERT_BASE_HIDDEN_DIM)


@unittest.skipIf(not has_torch, "torch not installed")
def test_bert_model(get_input_tensors):
    ids, token_type_ids, attention_mask = get_input_tensors
    NUM_MULTI_LABEL_COL = 4
    mock_bert = MockBertModel()
    get_dir = 'azureml.automl.dnn.nlp.classification.multilabel.bert_class.get_model_from_language'
    with patch(get_dir, return_value=("model_name", "model_path")):
        with patch('transformers.BertModel.from_pretrained', return_value=mock_bert):
            dataset_language = "some-language"
            model = BERTClass(dataset_language, NUM_MULTI_LABEL_COL)
            output_tensor = model(ids, token_type_ids=token_type_ids, mask=attention_mask)
            assert torch.is_tensor(output_tensor)
            assert output_tensor.size() == torch.Size([1, NUM_MULTI_LABEL_COL])


@unittest.skipIf(not has_torch, "torch not installed")
def test_bert_model_batch(get_input_tensors):
    ids, token_type_ids, attention_mask = get_input_tensors
    ids_batch = torch.cat([ids, ids], axis=0)
    token_type_ids_batch = torch.cat([token_type_ids, token_type_ids], axis=0)
    attention_mask_batch = torch.cat([attention_mask, attention_mask], axis=0)
    NUM_MULTI_LABEL_COL = 4
    mock_bert = MockBertModel()
    get_dir = 'azureml.automl.dnn.nlp.classification.multilabel.bert_class.get_model_from_language'
    with patch(get_dir, return_value=("model_name", "model_path")):
        with patch('transformers.BertModel.from_pretrained', return_value=mock_bert):
            dataset_language = "some-language"
            model = BERTClass(dataset_language, NUM_MULTI_LABEL_COL)
            output_tensor = model(ids_batch, token_type_ids=token_type_ids_batch, mask=attention_mask_batch)
            assert output_tensor.size() == torch.Size([2, NUM_MULTI_LABEL_COL])


@unittest.skipIf(not has_torch, "torch not installed")
def test_bert_class_uses_cdn(get_input_tensors):
    ids, token_type_ids, attention_mask = get_input_tensors
    NUM_MULTI_LABEL_COL = 4
    mock_bert = MockBertModel()
    get_dir = 'azureml.automl.dnn.nlp.classification.multilabel.bert_class.get_model_from_language'
    with patch(get_dir, return_value=("model_name", "model_path")):
        with patch('transformers.BertModel.from_pretrained', return_value=mock_bert) as mock_downloader:
            dataset_language = "some-language"
            model = BERTClass(dataset_language, NUM_MULTI_LABEL_COL)
            model(ids, token_type_ids=token_type_ids, mask=attention_mask)
            mock_downloader.assert_called_with("model_path", return_dict=False)


@unittest.skipIf(not has_torch, "torch not installed")
def test_bert_class_no_cdn_throws_client_exception():
    NUM_MULTI_LABEL_COL = 4
    get_dir = 'azureml.automl.dnn.nlp.classification.multilabel.bert_class.get_model_from_language'
    with patch(get_dir, return_value=(None, None)):
        with pytest.raises(ClientException):
            dataset_language = "some-language"
            BERTClass(dataset_language, NUM_MULTI_LABEL_COL)
