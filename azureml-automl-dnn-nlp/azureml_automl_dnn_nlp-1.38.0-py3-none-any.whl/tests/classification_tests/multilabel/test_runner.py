import unittest
from unittest.mock import patch
import importlib

from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.dnn.nlp.classification.multilabel import runner

from ...mocks import MockRun

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


class MockTrainingSet:

    def __init__(self):
        self.tokenizer = "some_tokenizer"


class MockModel:

    def __init__(self):
        self.model_name = "some_model"


class MockTrainer:

    def __init__(self):
        self.n_train_called = 0
        self.train_called_last_with = None
        self.n_compute_called = 0
        self.compute_called_with = None
        self.tokenizer = "some_tokenizer"
        self.model = MockModel()

    def train(self, train_dataset):
        self.n_train_called = self.n_train_called + 1
        self.train_called_last_with = train_dataset
        return "some_model"

    def compute_metrics(self, valid_dataset):
        self.n_compute_called = self.n_compute_called + 1
        self.compute_called_with = valid_dataset
        metrics_dict = {
            "accuracy": 0.5,
            "f1_score_micro": 0.6,
            "f1_score_macro": 0.7
        }
        metrics_dict_with_thresholds = {
            "accuracy": [0.5],
            "precision": [0.6],
            "recall": [0.7]
        }
        return metrics_dict, metrics_dict_with_thresholds


class MockAutoMLSettings:
    def __init__(self, distributed, label_column_name):
        self.is_gpu = True
        self.dataset_id = "some_dataset_id"
        self.validation_dataset_id = "some_validation_dataset_id"
        self.label_column_name = label_column_name
        self.enable_distributed_dnn_training = distributed
        self.primary_metric = 'accuracy'
        self.featurization = "some_featurization"


class MultilabelRunnerTests(unittest.TestCase):
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.ModelWrapper", return_value=None)
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.PytorchTrainer")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.load_multilabel_dataset")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.initialize_log_server",
           return_value=MockAutoMLSettings(False, "labels"))
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.save_conda_yml", return_value="conda_path")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.save_model_wrapper", return_value="model_path")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.Run.get_context")
    def test_runner(
            self,
            run_mock,
            save_model_mock,
            save_conda_mock,
            initialize_log_server_mock,
            load_multilabel_dataset_mock,
            trainer_mock,
            model_wrapper_mock
    ):
        automl_settings = {"is_gpu": True,
                           "dataset_id": "some_training_set",
                           "validation_dataset_id": "some_validation_set",
                           "label_column_name": "labels",
                           "enable_distributed_dnn_training": False}

        mock_run = MockRun(label_column_name="labels")
        run_mock.return_value = mock_run

        mocked_training_set = MockTrainingSet()
        dataset_loader_return = (mocked_training_set, "some_validation_set", 3, "some_vectorizer")
        load_multilabel_dataset_mock.return_value = dataset_loader_return

        mocked_trainer = MockTrainer()
        trainer_mock.return_value = mocked_trainer

        # Call Run
        runner.run(automl_settings)

        self.assertEquals(len(mock_run.properties), 10)
        self.assertEquals(mock_run.properties['primary_metric'], 'accuracy')
        self.assertEquals(mock_run.properties['score'], 0.5)
        self.assertEquals(mock_run.properties['run_algorithm'], ModelNames.BERT_BASE_UNCASED)

        self.assertEquals(trainer_mock.call_args[0][1], "eng")
        self.assertEquals(mocked_trainer.train_called_last_with, mocked_training_set)
        self.assertEquals(mocked_trainer.compute_called_with, "some_validation_set")
        self.assertEquals(mocked_trainer.n_train_called, 1)
        self.assertEquals(mocked_trainer.n_compute_called, 1)

        self.assertEquals(mock_run.metrics["accuracy"], 0.5)
        self.assertEquals(mock_run.metrics["f1_score_micro"], 0.6)
        self.assertEquals(mock_run.metrics["f1_score_macro"], 0.7)

    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.initialize_log_server",
           return_value=MockAutoMLSettings(False, None))
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.Run.get_context")
    def test_runner_without_label_col(
            self,
            run_mock,
            initialize_log_server_mock
    ):
        automl_settings = {"is_gpu": True,
                           "dataset_id": "some_training_set",
                           "validation_dataset_id": "some_validation_set",
                           "label_column_name": None,
                           "enable_distributed_dnn_training": False}

        mock_run = MockRun()
        run_mock.return_value = mock_run

        # Call Run
        with self.assertRaises(ValidationException):
            runner.run(automl_settings)

        # Exception is raised and none of the trainer code gets executed
        self.assertEquals(len(mock_run.properties), 2)
        self.assertTrue(mock_run.metrics == {})

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.ModelWrapper", return_value=None)
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.HorovodDistributedTrainer")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.load_multilabel_dataset")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.initialize_log_server",
           return_value=MockAutoMLSettings(True, "labels"))
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.save_conda_yml", return_value="conda_path")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.save_model_wrapper", return_value="model_path")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.Run.get_context")
    def test_runner_distributed(
            self,
            run_mock,
            save_model_mock,
            save_conda_mock,
            initialize_log_server_mock,
            load_multilabel_dataset_mock,
            trainer_mock,
            model_wrapper_mock
    ):
        automl_settings = {"is_gpu": True,
                           "dataset_id": "some_training_set",
                           "validation_dataset_id": "some_validation_set",
                           "label_column_name": "labels",
                           "enable_distributed_dnn_training": True}

        mock_run = MockRun(label_column_name="labels")
        run_mock.return_value = mock_run

        mocked_training_set = MockTrainingSet()
        dataset_loader_return = (mocked_training_set, "some_validation_set", 3, "some_vectorizer")
        load_multilabel_dataset_mock.return_value = dataset_loader_return

        mocked_trainer = MockTrainer()
        trainer_mock.return_value = mocked_trainer

        # Call Run
        runner.run(automl_settings)

        self.assertEquals(len(mock_run.properties), 10)
        self.assertEquals(mock_run.properties['primary_metric'], 'accuracy')
        self.assertEquals(mock_run.properties['score'], 0.5)

        self.assertEquals(mocked_trainer.train_called_last_with, mocked_training_set)
        self.assertEquals(mocked_trainer.compute_called_with, "some_validation_set")
        self.assertEquals(mocked_trainer.n_train_called, 1)
        self.assertEquals(mocked_trainer.n_compute_called, 1)

        self.assertEquals(mock_run.metrics["accuracy"], 0.5)
        self.assertEquals(mock_run.metrics["f1_score_micro"], 0.6)
        self.assertEquals(mock_run.metrics["f1_score_macro"], 0.7)

    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.ModelWrapper", return_value=None)
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.PytorchTrainer")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.load_multilabel_dataset")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.initialize_log_server",
           return_value=MockAutoMLSettings(False, "labels"))
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.save_conda_yml", return_value="conda_path")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.save_model_wrapper", return_value="model_path")
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.Run.get_context")
    def test_runner_labeling_service(
            self,
            run_mock,
            save_model_mock,
            save_conda_mock,
            initialize_log_server_mock,
            load_multilabel_dataset_mock,
            trainer_mock,
            model_wrapper_mock
    ):
        automl_settings = {"is_gpu": True,
                           "dataset_id": "some_training_set",
                           "validation_dataset_id": "some_validation_set",
                           "label_column_name": "labels",
                           "enable_distributed_dnn_training": False}

        mock_run = MockRun(run_source="Labeling", label_column_name="labels", labeling_dataset_type="FileDataset")
        run_mock.return_value = mock_run

        mocked_training_set = MockTrainingSet()
        dataset_loader_return = (mocked_training_set, "some_validation_set", 3, "some_vectorizer")
        load_multilabel_dataset_mock.return_value = dataset_loader_return

        mocked_trainer = MockTrainer()
        trainer_mock.return_value = mocked_trainer

        # Call Run
        runner.run(automl_settings)

        self.assertEquals(len(mock_run.properties), 10)
        self.assertEquals(mock_run.properties['primary_metric'], 'accuracy')
        self.assertEquals(mock_run.properties['score'], 0.5)

        self.assertEquals(trainer_mock.call_args[0][1], "eng")
        self.assertEquals(mocked_trainer.train_called_last_with, mocked_training_set)
        self.assertEquals(mocked_trainer.compute_called_with, "some_validation_set")
        self.assertEquals(mocked_trainer.n_train_called, 1)
        self.assertEquals(mocked_trainer.n_compute_called, 1)

        self.assertEquals(mock_run.metrics["accuracy"], 0.5)
        self.assertEquals(mock_run.metrics["f1_score_micro"], 0.6)
        self.assertEquals(mock_run.metrics["f1_score_macro"], 0.7)

    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.initialize_log_server",
           return_value=MockAutoMLSettings(False, None))
    @patch("azureml.automl.dnn.nlp.classification.multilabel.runner.Run.get_context")
    def test_runner_without_validation_data(
            self,
            run_mock,
            initialize_log_server_mock
    ):
        automl_settings = {"is_gpu": True,
                           "dataset_id": "some_training_set",
                           "validation_dataset_id": None,
                           "label_column_name": "labels",
                           "enable_distributed_dnn_training": False}

        mock_run = MockRun()
        run_mock.return_value = mock_run

        # Call Run
        with self.assertRaises(ValidationException):
            runner.run(automl_settings)

        # Exception is raised and none of the trainer code gets executed
        self.assertEquals(len(mock_run.properties), 2)
        self.assertTrue(mock_run.metrics == {})
