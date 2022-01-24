import pytest
import unittest
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.ner import runner
from azureml.automl.core.shared.exceptions import ValidationException

from ..mocks import (
    aml_dataset_mock, file_dataset_mock, get_ner_labeling_df, MockRun, ner_trainer_mock
)


@pytest.mark.usefixtures('new_clean_dir')
class NERRunnerTests(unittest.TestCase):
    """Tests for NER trainer."""

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.runner.get_model_from_language")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.create_unique_dir")
    @patch("azureml.automl.dnn.nlp.ner.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.ner.runner.prepare_run_properties")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.ner.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run")
    def test_runner(
            self,
            run_mock,
            post_run_mock,
            conda_yml_mock,
            save_model_mock,
            prepare_run_mock,
            initialize_log_server_mock,
            unique_dir_mock,
            get_by_id_mock,
            language_mock,
            model_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.primary_metric = "accuracy"
        initialize_log_server_mock.return_value = mock_settings
        unique_dir_mock.return_value = "ner_data"

        # dataset get_by_id mock
        mock_file_dataset = file_dataset_mock()
        get_by_id_mock.return_value = mock_file_dataset

        # language mock
        language_mock.return_value = "bert-base-cased", "some_path"

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        self.assertEqual(model_mock.from_pretrained.call_args[0][0], "some_path")

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.get_model_from_language")
    @patch("azureml.automl.dnn.nlp.ner.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.ner.runner.prepare_run_properties")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.ner.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run.get_context")
    def test_runner_labeling_service(
            self,
            run_mock,
            post_run_mock,
            conda_yml_mock,
            save_model_mock,
            prepare_run_mock,
            initialize_log_server_mock,
            language_mock,
            get_by_id_mock,
            model_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockRun(
            run_source="Labeling"
        )
        run_mock.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.primary_metric = "accuracy"
        initialize_log_server_mock.return_value = mock_settings
        language_mock.return_value = "bert-base-cased", "some_path"

        # dataset get_by_id mock
        mock_dataset = aml_dataset_mock(get_ner_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()

    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run")
    def test_runner_without_validation_data(
            self,
            run_mock,
            initialize_log_server_mock,
            get_by_id_mock,
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": None
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = None
        mock_settings.primary_metric = "accuracy"
        initialize_log_server_mock.return_value = mock_settings

        # dataset get_by_id mock
        mock_file_dataset = file_dataset_mock()
        get_by_id_mock.return_value = mock_file_dataset

        # Test runner
        with self.assertRaises(ValidationException):
            runner.run(automl_settings)


if __name__ == "__main__":
    unittest.main()
