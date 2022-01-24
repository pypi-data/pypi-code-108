import os
import pytest
import unittest
from unittest.mock import MagicMock, patch, mock_open

import ast
import numpy as np

from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, Split
from azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper import (
    _convert_to_spans, generate_results_for_labeling_service, load_test_dataset_for_labeling_service
)
from ..mocks import aml_dataset_mock, get_ner_labeling_df


@pytest.mark.usefixtures('new_clean_dir')
class LabelingDataHelperTest(unittest.TestCase):
    """Tests for labeling data helper functions."""
    def __init__(self, *args, **kwargs):
        super(LabelingDataHelperTest, self).__init__(*args, **kwargs)

    @patch("azureml.core.Dataset.get_by_id")
    def test_load_test_dataset_for_labeling_service(self, get_by_id_mock):
        workspace_mock = MagicMock()
        dataset_id = "mock_dataset_id"
        ner_dir = "ner_dir"
        data_filename = DataLiterals.TEST_TEXT_FILENAME
        data_label = Split.test

        mock_dataset = aml_dataset_mock(get_ner_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        mock_text = "Nikolaus told a news\n\tbriefing, scientific study"
        converted_list = ["Nikolaus\n", "told\n", "a\n", "news\n", "briefing\n", ",\n", "scientific\n", "study\n"]
        open_mock = mock_open(read_data=mock_text)
        with patch("builtins.open", open_mock):
            load_test_dataset_for_labeling_service(workspace_mock, dataset_id, ner_dir, data_filename, data_label)
        self.assertTrue(os.path.join("ner_data", "sample1.txt") in open_mock.call_args_list[0][0][0])
        self.assertTrue(os.path.join("ner_data", "sample2.txt") in open_mock.call_args_list[2][0][0])
        self.assertEquals(open_mock.return_value.writelines.call_args_list[0][0][0], converted_list)

    def test_generate_results_for_labeling_service(self):
        predicted_labels = [['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'B-PER', 'I-PER', 'O']]
        score_list = np.random.rand(2, 5)
        predictions_output_file_path = os.path.join(
            OutputLiterals.OUTPUT_DIR, OutputLiterals.PREDICTIONS_TXT_FILE_NAME
        )
        first_file_name = "file1.txt"
        second_file_name = "file2.txt"
        predictions_first_file = self.get_mock_prediction_list(
            predicted_labels[0], score_list[0]
        )
        predictions_second_file = self.get_mock_prediction_list(
            predicted_labels[1], score_list[1], ["a", "news", "briefing", "scientific", "study"]
        )
        mock_text = self.get_mock_predictions_text(predicted_labels, score_list)
        open_mock = mock_open(read_data=mock_text)
        mock_convert_to_spans = MagicMock()
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.os.remove"):
            with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
                with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper._convert_to_spans",
                           mock_convert_to_spans):
                    generate_results_for_labeling_service(
                        predictions_output_file_path,
                        [first_file_name, second_file_name]
                    )
        self.assertTrue(open_mock.call_count == 1)
        self.assertEquals(mock_convert_to_spans.call_args_list[0][0][0], predictions_first_file)
        self.assertEquals(mock_convert_to_spans.call_args_list[0][0][1], first_file_name)
        self.assertEquals(mock_convert_to_spans.call_args_list[0][0][2], predictions_output_file_path)
        self.assertEquals(mock_convert_to_spans.call_args_list[1][0][0], predictions_second_file)
        self.assertEquals(mock_convert_to_spans.call_args_list[1][0][1], second_file_name)
        self.assertEquals(mock_convert_to_spans.call_args_list[1][0][2], predictions_output_file_path)

    def test_convert_to_spans_all_O(self):
        predicted_labels = np.full(5, 'O')
        mock_prediction = self.get_mock_prediction_list(predicted_labels)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_data/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'], [])
        self.assertEquals(written_msg['label_confidence'], [])

    def test_convert_to_spans_one_B_I_set(self):
        predicted_labels = ['O', 'B-PER', 'I-PER', 'I-PER', 'O']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_data/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'], [{'label': 'PER', 'offsetStart': 9, 'offsetEnd': 20}])
        self.assertEquals(written_msg['label_confidence'], [score_list[1]])

    def test_convert_to_spans_multiple_B_I_set(self):
        predicted_labels = ['B-PER', 'B-PER', 'I-PER', 'I-PER', 'B-PER']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_data/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 8})
        self.assertEquals(written_msg['label'][1], {'label': 'PER', 'offsetStart': 9, 'offsetEnd': 20})
        self.assertEquals(written_msg['label'][2], {'label': 'PER', 'offsetStart': 20, 'offsetEnd': 24})
        self.assertEquals(written_msg['label_confidence'], [score_list[0], score_list[1], score_list[4]])

    def test_convert_to_spans_I_before_B(self):
        predicted_labels = ['o', 'I-PER', 'B-PER', 'I-PER', 'o']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_data/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 9, 'offsetEnd': 12})
        self.assertEquals(written_msg['label'][1], {'label': 'PER', 'offsetStart': 13, 'offsetEnd': 20})
        self.assertEquals(written_msg['label_confidence'], [score_list[1], score_list[2]])

    def test_convert_to_spans_labels_not_in_order(self):
        predicted_labels = ['B-PER', 'I-LOC', 'I-PER', 'B-LOC', 'I-LOC']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_data/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 8})
        self.assertEquals(written_msg['label'][1], {'label': 'LOC', 'offsetStart': 9, 'offsetEnd': 12})
        self.assertEquals(written_msg['label'][2], {'label': 'PER', 'offsetStart': 13, 'offsetEnd': 16})
        self.assertEquals(written_msg['label'][3], {'label': 'LOC', 'offsetStart': 17, 'offsetEnd': 24})
        self.assertEquals(
            written_msg['label_confidence'], [score_list[0], score_list[1], score_list[2], score_list[3]]
        )

    def test_convert_to_spans_labels_not_in_order_with_special_token(self):
        predicted_labels = ['B-PER', 'I-LOC', 'I-PER', 'B-LOC', 'I-LOC']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list, special_token=True)
        mock_test_text = self.get_mock_test_file_text(special_token=True)
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_data/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        print(written_msg)
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 9})
        self.assertEquals(written_msg['label'][1], {'label': 'LOC', 'offsetStart': 10, 'offsetEnd': 14})
        self.assertEquals(written_msg['label'][2], {'label': 'PER', 'offsetStart': 15, 'offsetEnd': 19})
        self.assertEquals(written_msg['label'][3], {'label': 'LOC', 'offsetStart': 20, 'offsetEnd': 29})
        self.assertEquals(
            written_msg['label_confidence'], [score_list[0], score_list[1], score_list[2], score_list[3]]
        )

    @staticmethod
    def get_mock_prediction_list(predicted_labels, score_list=None, text_list=None, special_token=False):
        # Return a prediction list containing a set of text + predicted label + score
        text_list = ["Nikolaus", "van", "der", "Pas", "told"] if text_list is None else text_list
        if special_token:
            text_list = [token + "\ufffd" for token in text_list]  # \ufffd is what appears by setting errors=replace
        score_list = np.random.rand(5) if score_list is None else score_list

        for i in range(len(text_list)):
            text_list[i] = text_list[i] + " " + predicted_labels[i] + " " + str(score_list[i])

        return text_list

    @staticmethod
    def get_mock_predictions_text(predicted_labels, score_list=None):
        # Return a set of predictions text where each text are separated by '\n'
        text_list = [["Nikolaus", "van", "der", "Pas", "told"], ["a", "news", "briefing", "scientific", "study"]]
        score_list = np.random.rand(2, 5) if score_list is None else score_list

        result_text = ""
        for i in range(len(text_list)):
            for j in range(len(text_list[i])):
                result_text += text_list[i][j] + " " + predicted_labels[i][j] + " " + str(score_list[i][j]) + "\n"
            result_text += "\n"

        return result_text

    @staticmethod
    def get_mock_test_file_text(special_token=False):
        # Return a prediction text containing a set of text
        text_list = ["Nikolaus", "van", "der", "Pas", "told"]
        if special_token:
            text_list = [token + "\ufffd" for token in text_list]
        text = '\n'.join([' '.join(text_list[:-1]), text_list[-1]])
        return text


if __name__ == "__main__":
    unittest.main()
