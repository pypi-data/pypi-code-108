import pandas as pd
import pytest
import unittest
from pandas.util.testing import assert_frame_equal
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer import MultilabelInferencer
from azureml.automl.dnn.nlp.classification.io.read.dataloader import get_vectorizer
from azureml.automl.dnn.nlp.common.constants import DataLiterals, SystemSettings

from ...mocks import (
    aml_dataset_mock, get_multilabel_labeling_df, MockBertClass, MockRun, open_classification_file
)

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


class TestMultilabelInferencer:
    @pytest.mark.usefixtures('MultilabelDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [False, True])
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_obtain_dataloader(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        run = MockRun()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MultilabelInferencer(run, device)
        dataset_language = "some_lanuage"
        inference_data_loader = inferencer.obtain_dataloader(input_df, dataset_language, label_column_name)
        assert len(inference_data_loader.dataset) == len(input_df)

    @pytest.mark.usefixtures('MultilabelDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [False, True])
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_predict(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        vectorizer = get_vectorizer(input_df, input_df, label_column_name)
        num_label_cols = len(vectorizer.get_feature_names())
        assert num_label_cols == 6
        run = MockRun()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MultilabelInferencer(run, device)
        dataset_language = "some_lanuage"
        inference_data_loader = inferencer.obtain_dataloader(input_df, dataset_language, label_column_name)
        assert len(inference_data_loader.dataset) == len(input_df)
        model = MockBertClass(num_label_cols)
        predicted_df = inferencer.predict(model, vectorizer, input_df, inference_data_loader, label_column_name)
        assert len(predicted_df) == len(input_df)

    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.save_predicted_results")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.MultilabelInferencer.predict")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.load_model_wrapper")
    @pytest.mark.usefixtures('MultilabelDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [False, True])
    def test_score(
            self,
            load_model_wrapper_mock, get_by_id_mock, predict_mock, save_predicted_results_mock,
            MultilabelDatasetTester
    ):
        label_column_name = "label"
        mock_run = MockRun(
            label_column_name=label_column_name
        )
        mock_model_wrapper = MagicMock()
        mock_model_wrapper.dataset_language.return_value = "eng"
        load_model_wrapper_mock.return_value = mock_model_wrapper

        input_df = MultilabelDatasetTester.get_data().copy()
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset

        predicted_df = pd.DataFrame(
            [['A,a,1,2,label5,label6', '0.1,0.2,0.3,0.4,0.5,0.6'] for i in range(5)],
            columns=[label_column_name, DataLiterals.LABEL_CONFIDENCE]
        )
        predict_mock.return_value = predicted_df

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MultilabelInferencer(mock_run, device)

        with patch("azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper.open",
                   new=open_classification_file):
            output_df = inferencer.score(input_dataset_id="some_dataset_id")

        assert_frame_equal(predicted_df, output_df)
        assert predict_mock.call_count == 1
        assert save_predicted_results_mock.call_count == 1

    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer."
           "generate_predictions_output_for_labeling_service")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.MultilabelInferencer.predict")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.load_model_wrapper")
    def test_score_labeling_service(
            self, load_model_wrapper_mock, get_by_id_mock, predict_mock, generate_output_mock
    ):
        label_column_name = "label"
        mock_run = MockRun(
            run_source=SystemSettings.LABELING_RUNSOURCE,
            label_column_name=label_column_name,
            labeling_dataset_type="FileDataset"
        )
        mock_model_wrapper = MagicMock()
        mock_model_wrapper.dataset_language.return_value = "eng"
        load_model_wrapper_mock.return_value = mock_model_wrapper

        mock_aml_dataset = aml_dataset_mock(get_multilabel_labeling_df())
        get_by_id_mock.return_value = mock_aml_dataset

        predicted_df = pd.DataFrame(
            [
                ["label_1,label_2", '0.758,0.323'],
                ["label_1,label_2", '0.831,0.418']
            ],
            columns=[DataLiterals.LABEL_COLUMN, DataLiterals.LABEL_CONFIDENCE]
        )
        predict_mock.return_value = predicted_df

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MultilabelInferencer(mock_run, device)

        with patch("azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper.open",
                   new=open_classification_file):
            output_df = inferencer.score(input_dataset_id="some_dataset_id")

        assert_frame_equal(predicted_df, output_df)
        assert predict_mock.call_count == 1
        assert generate_output_mock.call_count == 1

    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.DataLoader")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.PyTorchDatasetWrapper")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.save_predicted_results")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.MultilabelInferencer.predict")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer.load_model_wrapper")
    @patch("azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer."
           "is_data_labeling_run_with_file_dataset")
    @pytest.mark.usefixtures('MultilabelDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [False, True])
    @pytest.mark.parametrize('enable_datapoint_id_output', [True, False])
    def test_score_enable_datapoint_id_output(
            self, is_data_labeling_run_with_file_dataset_mock, load_model_wrapper_mock,
            get_by_id_mock, predict_mock, save_predicted_results_mock, datasetwrapper_mock,
            dataloader_mock, MultilabelDatasetTester, enable_datapoint_id_output
    ):
        # Labeling run but tabular dataset input
        is_data_labeling_run_with_file_dataset_mock.return_value = False

        label_column_name = "labels_col"
        mock_run = MockRun(
            run_source=SystemSettings.LABELING_RUNSOURCE,
            label_column_name=label_column_name,
            labeling_dataset_type="TabularDataset"
        )
        mock_model_wrapper = MagicMock()
        mock_model_wrapper.dataset_language.return_value = "eng"
        load_model_wrapper_mock.return_value = mock_model_wrapper

        input_df = MultilabelDatasetTester.get_data().copy()
        input_df[DatasetLiterals.DATAPOINT_ID] = ["id_1", "id_2", "id_3", "id_4", "id_5"]
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset
        datasetwrapper_mock.return_value = MagicMock()

        predicted_df = pd.DataFrame(
            [['A,a,1,2,label5,label6', '0.1,0.2,0.3,0.4,0.5,0.6'] for i in range(5)],
            columns=[label_column_name, DataLiterals.LABEL_CONFIDENCE]
        )
        predict_mock.return_value = predicted_df

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MultilabelInferencer(mock_run, device)

        with patch("azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper.open",
                   new=open_classification_file):
            output_df = inferencer.score(input_dataset_id="some_dataset_id",
                                         enable_datapoint_id_output=enable_datapoint_id_output)

        if enable_datapoint_id_output:
            assert sorted(output_df.columns) == sorted([DatasetLiterals.DATAPOINT_ID,
                                                        label_column_name, "label_confidence"])
            assert output_df[DatasetLiterals.DATAPOINT_ID].equals(input_df[DatasetLiterals.DATAPOINT_ID])
        else:
            assert sorted(output_df.columns) == sorted([label_column_name, "label_confidence"])
        assert sorted(datasetwrapper_mock.call_args[0][0].columns) == sorted(
            input_df.columns.difference([label_column_name, DatasetLiterals.DATAPOINT_ID]))
        assert dataloader_mock.call_count == 1
        assert predict_mock.call_count == 1
        assert save_predicted_results_mock.call_count == 1
