import pytest
import transformers

from azureml.automl.dnn.nlp.common.constants import Split
from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import DatasetWrapper


@pytest.mark.usefixtures('new_clean_dir')
class TestDatasetWrapper:
    @pytest.mark.parametrize('split', [Split.train, Split.test, Split.valid])
    def test_dataset_with_labels(self, split, get_tokenizer):
        max_seq_length = 20
        mode = split

        data = "Commissioner O\nFranz B-PER\nFischler I-PER\n\nproposed O\nBritain B-LOC\n"
        test_dataset = DatasetWrapper(
            data=data,
            tokenizer=get_tokenizer,
            labels=["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
            max_seq_length=max_seq_length,
            mode=mode
        )
        assert len(test_dataset) == 2
        for test_example in test_dataset:
            assert type(test_example) == transformers.tokenization_utils_base.BatchEncoding
            assert len(test_example.input_ids) == max_seq_length
            assert len(test_example.attention_mask) == max_seq_length
            assert len(test_example.token_type_ids) == max_seq_length
            assert len(test_example.label_ids) == max_seq_length
            assert any(i >= 0 for i in test_example.label_ids)

    def test_dataset_without_labels_for_test_input(self, get_tokenizer):
        max_seq_length = 20
        mode = Split.test

        data = "Commissioner\nFranz\nFischler\n\nproposed\nBritain\n"
        test_dataset = DatasetWrapper(
            data=data,
            tokenizer=get_tokenizer,
            labels=["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
            max_seq_length=max_seq_length,
            mode=mode
        )
        assert len(test_dataset) == 2
        assert not test_dataset.include_label
        for test_example in test_dataset:
            assert type(test_example) == transformers.tokenization_utils_base.BatchEncoding
            assert len(test_example.input_ids) == max_seq_length
            assert len(test_example.attention_mask) == max_seq_length
            assert len(test_example.token_type_ids) == max_seq_length
            assert len(test_example.label_ids) == max_seq_length
            assert any(i >= 0 for i in test_example.label_ids)
