import pytest
import unittest
from unittest.mock import mock_open, patch

import numpy as np
import os

from azureml.automl.dnn.nlp.ner._utils import get_labels, write_predictions_to_file, create_unique_dir


@pytest.mark.usefixtures('new_clean_dir')
class UtilsTest(unittest.TestCase):
    """Tests for NER trainer."""
    def __init__(self, *args, **kwargs):
        super(UtilsTest, self).__init__(*args, **kwargs)

    def test_get_labels(self):
        labels = get_labels('ner_data/labels_misc.txt')
        self.assertEqual(set(labels), set(["O", "Aditya", "Anup", "Arjun", "Harsh"]))
        labels = get_labels(None)
        self.assertEqual(
            set(labels), set(["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"])
        )

    def test_write_predictions_to_file_no_label(self):
        mock_text = "Commissioner\nFranz\nFischler\n\nproposed\nBritain\n"
        mock_text_list = [["Commissioner", "Franz", "Fischler"], ["proposed", "Britain"]]
        preds_list = [['O', 'B-PER', 'I-PER'], ['O', 'B-LOC']]
        preds_proba_list = [np.random.rand(3).tolist(), np.random.rand(2).tolist()]

        mock_text_list_1d = sum(mock_text_list, [])
        preds_list_1d = sum(preds_list, [])
        preds_proba_list_1d = sum(preds_proba_list, [])

        actual_output_path = os.path.join('ner_data', 'actual_test_writer.txt')
        test_path = os.path.join('ner_data', "sample_test.txt")
        open_mock = mock_open(read_data=mock_text)
        with patch("builtins.open", open_mock):
            write_predictions_to_file(
                actual_output_path, test_path, preds_list, preds_proba_list
            )
        self.assertIsNotNone(open_mock.call_count == 2)

        idx = 0
        write_str = mock_text_list_1d[0] + " " + preds_list_1d[0] + " " + str(preds_proba_list_1d[0]) + "\n"
        for mock_calls in open_mock.mock_calls:
            if mock_calls[0] == '().write':
                if mock_calls[1][0] == "\n":
                    continue
                self.assertEquals(mock_calls[1][0], write_str)
                if len(mock_text_list_1d) - 1 == idx:
                    break
                idx += 1
                write_str = \
                    mock_text_list_1d[idx] + " " + preds_list_1d[idx] + " " + str(preds_proba_list_1d[idx]) + "\n"

    def test_write_predictions_to_file_with_label(self):
        mock_text = "Commissioner O\nFranz B-PER\nFischler I-PER\n\nproposed O\nBritain B-LOC\n"
        mock_text_list = [["Commissioner", "Franz", "Fischler"], ["proposed", "Britain"]]
        preds_list = [['O', 'B-PER', 'I-PER'], ['O', 'B-LOC']]
        preds_proba_list = [np.random.rand(3).tolist(), np.random.rand(2).tolist()]

        mock_text_list_1d = sum(mock_text_list, [])
        preds_list_1d = sum(preds_list, [])
        preds_proba_list_1d = sum(preds_proba_list, [])

        actual_output_path = os.path.join('ner_data', 'actual_test_writer.txt')
        test_path = os.path.join('ner_data', "sample_test.txt")
        open_mock = mock_open(read_data=mock_text)
        with patch("builtins.open", open_mock):
            write_predictions_to_file(
                actual_output_path, test_path, preds_list, preds_proba_list
            )
        self.assertIsNotNone(open_mock.call_count == 2)

        idx = 0
        write_str = mock_text_list_1d[0] + " " + preds_list_1d[0] + " " + str(preds_proba_list_1d[0]) + "\n"
        for mock_calls in open_mock.mock_calls:
            if mock_calls[0] == '().write':
                if mock_calls[1][0] == "\n":
                    continue
                self.assertEquals(mock_calls[1][0], write_str)
                if len(mock_text_list_1d) - 1 == idx:
                    break
                idx += 1
                write_str = \
                    mock_text_list_1d[idx] + " " + preds_list_1d[idx] + " " + str(preds_proba_list_1d[idx]) + "\n"

    def create_unique_dir(self):
        with patch("os.makedirs", return_val=None):
            dir1 = create_unique_dir("some_dir")
            dir2 = create_unique_dir("some_dir")
            dir3 = create_unique_dir("some_dir")
            dir4 = create_unique_dir("some_dir")

        assert "some_dir" in dir1
        assert "some_dir" in dir2
        assert "some_dir" in dir3
        assert "some_dir" in dir4

        assert dir1 != dir2
        assert dir2 != dir3
        assert dir3 != dir4
