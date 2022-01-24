import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.classification.io.read.dataloader import load_multiclass_dataset
from azureml.automl.dnn.nlp.classification.multiclass.trainer import TextClassificationTrainer
from ...mocks import multiclass_trainer_mock, aml_dataset_mock


@pytest.mark.usefixtures('MulticlassDatasetTester')
@pytest.mark.usefixtures('MulticlassValDatasetTester')
@pytest.mark.usefixtures('MulticlassTokenizer')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('include_label_col', [True])
@pytest.mark.parametrize('enable_distributed', [True, False])
class TestTextClassificationTrainerTests:
    """Tests for Text Classification trainer."""
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoConfig")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.DistributedTrainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.get_model_from_language")
    @patch("azureml.core.Dataset.get_by_id")
    def test_train_valid(self, get_by_id_mock, language_mock, distributed_trainer_mock, trainer_mock, auto_config,
                         auto_tokenizer, auto_model_mock, MulticlassDatasetTester, MulticlassValDatasetTester,
                         enable_distributed, MulticlassTokenizer):
        train_df = MulticlassDatasetTester.get_data().copy()
        validation_df = MulticlassValDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        concat_df = pd.concat([train_df, validation_df], ignore_index=True)
        mock_aml_dataset = aml_dataset_mock(concat_df)
        get_by_id_mock.return_value = mock_aml_dataset
        training_set, validation_set, label_list, _, _, _ = load_multiclass_dataset(
            "dataset_id", "val_dataset_id", label_column_name, "workspace", MulticlassTokenizer)

        language_mock.return_value = ('some_model_name', "some_model_path")

        auto_config.from_pretrained.return_value = MagicMock()
        auto_tokenizer.from_pretrained.return_value = MagicMock()
        auto_model_mock.from_pretrained.return_value = MagicMock()

        trainer_multiclass = TextClassificationTrainer(label_list, "eng", enable_distributed=enable_distributed)

        # trainer mock
        mock_trainer = multiclass_trainer_mock(len(concat_df))
        distributed_mock_trainer = multiclass_trainer_mock(len(concat_df))
        trainer_mock.return_value = mock_trainer
        distributed_trainer_mock.return_value = distributed_mock_trainer

        trainer_multiclass.train(training_set)

        # train function
        trainer_multiclass.trainer.train.assert_called_once()
        trainer_multiclass.trainer.save_model.assert_called_once()
        trainer_multiclass.trainer.save_state.assert_called_once()

        # validate function
        predictions = trainer_multiclass.validate(validation_set)
        trainer_multiclass.trainer.predict.assert_called_once()
        assert predictions.shape == (len(concat_df), len(label_list))
        trainer_multiclass.trainer.save_metrics.assert_called_once()
        assert auto_config.from_pretrained.call_args[0][0] == 'some_model_name'
        assert auto_tokenizer.from_pretrained.call_args[0][0] == 'some_model_name'
        assert auto_model_mock.from_pretrained.call_args[0][0] == 'some_model_path'

        if enable_distributed is True:
            assert trainer_multiclass.trainer is distributed_mock_trainer
