import json
import os
import numpy as np
import pandas as pd
import unittest
from pandas.util.testing import assert_frame_equal
from unittest.mock import MagicMock, mock_open, patch

from azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper import (
    format_multilabel_predicted_df,
    generate_predictions_output_for_labeling_service,
    load_dataset_for_labeling_service, load_datasets_for_labeling_service
)
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, Split

from ...mocks import (
    aml_dataset_mock, get_multilabel_labeling_df, get_multiclass_labeling_df, open_classification_file
)


class ClassificationLabelingDataHelperTest(unittest.TestCase):
    """Tests for labeling data helper functions."""

    def __init__(self, *args, **kwargs):
        super(ClassificationLabelingDataHelperTest, self).__init__(*args, **kwargs)

    @patch("azureml.core.Dataset.get_by_id")
    def test_load_datasets_for_labeling_service_multilabel(self, get_by_id_mock):
        workspace_mock = MagicMock()
        dataset_id = "mock_dataset_id"
        validation_dataset_id = "mock_validation_dataset_id"
        download_dir = DataLiterals.DATA_DIR
        include_label = True

        mock_dataset = aml_dataset_mock(get_multilabel_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        with patch("builtins.open", new=open_classification_file):
            train_df, validation_df = load_datasets_for_labeling_service(
                workspace_mock, dataset_id, validation_dataset_id, download_dir, include_label
            )

        expected_df = pd.DataFrame(
            [
                ["Example text content 1. Multiple sentences.", "['label_1', 'label_2']"],
                ["Example text content 2.", "[]"],
                ["Example text content 3, comma separated.", "['label_1']"]
            ],
            columns=[DataLiterals.TEXT_COLUMN, DataLiterals.LABEL_COLUMN]
        )
        self.assertIsNone(assert_frame_equal(expected_df, train_df))
        self.assertIsNone(assert_frame_equal(expected_df, validation_df))

    @patch("azureml.core.Dataset.get_by_id")
    def test_load_dataset_for_labeling_service_multilabel(self, get_by_id_mock):
        workspace_mock = MagicMock()
        dataset_id = "mock_dataset_id"
        download_dir = DataLiterals.DATA_DIR
        include_label = True
        data_label = Split.train

        mock_dataset = aml_dataset_mock(get_multilabel_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        with patch("builtins.open", new=open_classification_file):
            result_df, input_file_paths = load_dataset_for_labeling_service(
                workspace_mock, dataset_id, download_dir, include_label, data_label
            )

        expected_df = pd.DataFrame(
            [
                ["Example text content 1. Multiple sentences.", "['label_1', 'label_2']"],
                ["Example text content 2.", "[]"],
                ["Example text content 3, comma separated.", "['label_1']"]
            ],
            columns=[DataLiterals.TEXT_COLUMN, DataLiterals.LABEL_COLUMN]
        )
        self.assertIsNone(assert_frame_equal(expected_df, result_df))
        expected_input_file_paths = []
        for entry in get_multilabel_labeling_df()['image_url']:
            expected_input_file_paths.append(os.path.join(entry.arguments['datastoreName'], entry.resource_identifier))
        self.assertEquals(sorted(input_file_paths), sorted(expected_input_file_paths))

    @patch("azureml.core.Dataset.get_by_id")
    def test_load_dataset_for_labeling_service_multilabel_exclude_label(self, get_by_id_mock):
        workspace_mock = MagicMock()
        dataset_id = "mock_dataset_id"
        download_dir = DataLiterals.DATA_DIR
        include_label = False
        data_label = Split.train

        mock_dataset = aml_dataset_mock(get_multilabel_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        with patch("builtins.open", new=open_classification_file):
            result_df, input_file_paths = load_dataset_for_labeling_service(
                workspace_mock, dataset_id, download_dir, include_label, data_label
            )

        expected_df = pd.DataFrame(
            [
                ["Example text content 1. Multiple sentences."],
                ["Example text content 2."],
                ["Example text content 3, comma separated."]
            ],
            columns=[DataLiterals.TEXT_COLUMN]
        )
        self.assertIsNone(assert_frame_equal(expected_df, result_df))
        expected_input_file_paths = []
        for entry in get_multilabel_labeling_df()['image_url']:
            expected_input_file_paths.append(os.path.join(entry.arguments['datastoreName'], entry.resource_identifier))
        self.assertEquals(sorted(input_file_paths), sorted(expected_input_file_paths))

    @patch("azureml.core.Dataset.get_by_id")
    def test_load_dataset_for_labeling_service_multiclass(self, get_by_id_mock):
        workspace_mock = MagicMock()
        dataset_id = "mock_dataset_id"
        download_dir = DataLiterals.DATA_DIR
        include_label = True
        data_label = Split.train

        mock_dataset = aml_dataset_mock(get_multiclass_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        with patch("builtins.open", new=open_classification_file):
            result_df, _ = load_dataset_for_labeling_service(
                workspace_mock, dataset_id, download_dir, include_label, data_label
            )

        expected_df = pd.DataFrame(
            [
                ["Example text content 1. Multiple sentences.", "label_1"],
                ["Example text content 2.", "label_2"],
                ["Example text content 3, comma separated.", "label_3"]
            ],
            columns=[DataLiterals.TEXT_COLUMN, DataLiterals.LABEL_COLUMN]
        )
        self.assertIsNone(assert_frame_equal(expected_df, result_df))

    @patch("azureml.core.Dataset.get_by_id")
    def test_load_dataset_for_labeling_service_multiclass_exclude_label(self, get_by_id_mock):
        workspace_mock = MagicMock()
        dataset_id = "mock_dataset_id"
        download_dir = DataLiterals.DATA_DIR
        include_label = False
        data_label = Split.train

        mock_dataset = aml_dataset_mock(get_multiclass_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        with patch("builtins.open", new=open_classification_file):
            result_df, _ = load_dataset_for_labeling_service(
                workspace_mock, dataset_id, download_dir, include_label, data_label
            )

        expected_df = pd.DataFrame(
            [
                ["Example text content 1. Multiple sentences."],
                ["Example text content 2."],
                ["Example text content 3, comma separated."]
            ],
            columns=[DataLiterals.TEXT_COLUMN]
        )
        self.assertIsNone(assert_frame_equal(expected_df, result_df))

    def test_format_multilabel_predicted_df(self):
        label_column_name = "label"
        df = pd.DataFrame([["a,b,c", "0.1,0.3,0.2"], ["a,b,c", "0.5,0.1,0.2"]],
                          columns=[label_column_name, DataLiterals.LABEL_CONFIDENCE])
        new_df = format_multilabel_predicted_df(df, label_column_name)
        self.assertEquals(new_df[label_column_name][0], ["a", "b", "c"])
        self.assertEquals(new_df[label_column_name][1], ["a", "b", "c"])
        self.assertEquals(new_df[DataLiterals.LABEL_CONFIDENCE][0], [0.1, 0.3, 0.2])
        self.assertEquals(new_df[DataLiterals.LABEL_CONFIDENCE][1], [0.5, 0.1, 0.2])

    def generate_predictions_output_for_labeling_service_helper(self, predictions_df, input_file_paths):
        open_mock = mock_open()

        with patch("builtins.open", open_mock):
            generate_predictions_output_for_labeling_service(
                predictions_df, input_file_paths,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME, DataLiterals.LABEL_COLUMN
            )

        counter = 0
        for i in range(len(predictions_df)):
            actual_entry = json.loads(open_mock.return_value.write.call_args_list[counter][0][0])
            self.assertEquals(len(actual_entry), 3)
            text_file_full_path = DataLiterals.DATASTORE_PREFIX + input_file_paths[i]
            self.assertEquals(actual_entry["image_url"], text_file_full_path)
            self.assertEquals(actual_entry[DataLiterals.LABEL_COLUMN],
                              predictions_df[DataLiterals.LABEL_COLUMN][i])
            self.assertEquals(actual_entry[DataLiterals.LABEL_CONFIDENCE],
                              predictions_df[DataLiterals.LABEL_CONFIDENCE][i])
            self.assertEquals(open_mock.return_value.write.call_args_list[counter + 1][0][0], '\n')
            counter += 2

    def test_generate_predictions_output_for_labeling_service_multiclass(self):
        predictions_df = pd.DataFrame(
            [
                ["label_1", np.float32(0.758)],
                ["label_2", 0.831]
            ],
            columns=[DataLiterals.LABEL_COLUMN, DataLiterals.LABEL_CONFIDENCE]
        )
        image_url1 = os.path.join("datastore", "1.txt")
        image_url2 = os.path.join("datastore", "2.txt")
        input_file_paths = [image_url1, image_url2]
        self.generate_predictions_output_for_labeling_service_helper(predictions_df, input_file_paths)

    def test_generate_predictions_output_for_labeling_service_multilabel(self):
        predictions_df = pd.DataFrame(
            [
                [["label_1", "label_2"], [0.758, 0.323]],
                [["label_1", "label_2"], [0.831, 0.418]]
            ],
            columns=[DataLiterals.LABEL_COLUMN, DataLiterals.LABEL_CONFIDENCE]
        )
        image_url1 = os.path.join("datastore", "1.txt")
        image_url2 = os.path.join("datastore", "2.txt")
        input_file_paths = [image_url1, image_url2]
        self.generate_predictions_output_for_labeling_service_helper(predictions_df, input_file_paths)

    def test_generate_predictions_output_for_labeling_service_extra_columns(self):
        predictions_df = pd.DataFrame(
            [
                ["text 1", "label_1", 0.758],
                ["text 2", "label_2", 0.831]
            ],
            columns=["text", DataLiterals.LABEL_COLUMN, DataLiterals.LABEL_CONFIDENCE]
        )
        input_file_paths = [os.path.join("datastore", "1.txt"), os.path.join("datastore", "2.txt")]
        self.generate_predictions_output_for_labeling_service_helper(predictions_df, input_file_paths)
