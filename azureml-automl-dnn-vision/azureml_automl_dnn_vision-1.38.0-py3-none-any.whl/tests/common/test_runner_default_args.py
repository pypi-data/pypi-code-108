import tempfile
from unittest.mock import patch, MagicMock, DEFAULT

from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.automl.dnn.vision.classification import runner as runner_classification
from azureml.automl.dnn.vision.object_detection import runner as runner_od
from azureml.core import Experiment
from azureml.core.run import _OfflineRun, Run


@patch('azureml.automl.dnn.vision.classification.runner.utils.download_required_files')
@patch('azureml.automl.dnn.vision.classification.runner.train')
@patch('azureml.automl.dnn.vision.classification.runner.distributed_utils.master_process')
def test_classification_runner_defaults_to_ignore_data_errors(mock_download, mock_train_model, mock_master_process):
    mock_download.return_value = None
    mock_master_process.return_value = False

    mock_run = get_mock_run()

    def side_effect(*args, **kwargs):
        assert kwargs[SettingsLiterals.IGNORE_DATA_ERRORS] is True
        return DEFAULT

    with patch.object(Run, 'get_context', return_value=mock_run):
        with patch('azureml.automl.dnn.vision.classification.io.read.utils.AmlDatasetWrapper',
                   autospec=True, create=True) as AmlDatasetWrapperMock:
            with tempfile.TemporaryDirectory() as tmp_output_dir:
                AmlDatasetWrapperMock.side_effect = side_effect
                settings = {'output_dir': tmp_output_dir,
                            SettingsLiterals.DATASET_ID: 'test_dataset_id',
                            SettingsLiterals.VALIDATION_DATASET_ID: 'test_dataset_id',
                            SettingsLiterals.TASK_TYPE: 'some_task_type'}
                runner_classification.run(settings)


@patch('azureml.automl.dnn.vision.object_detection.runner.utils.download_required_files')
@patch('azureml.automl.dnn.vision.object_detection.runner.read_aml_dataset')
def test_od_runner_defaults_to_ignore_data_errors(mock_read_aml_dataset, mock_download):
    mock_download.return_value = None

    mock_run = get_mock_run()

    side_effect_passed = False

    def side_effect(*args, **kwargs):
        nonlocal side_effect_passed

        assert kwargs[SettingsLiterals.IGNORE_DATA_ERRORS] is True

        side_effect_passed = True

        return DEFAULT

    mock_read_aml_dataset.side_effect = side_effect

    with patch.object(Run, 'get_context', return_value=mock_run):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            settings = {'output_dir': tmp_output_dir,
                        SettingsLiterals.DATASET_ID: 'test_dataset_id',
                        SettingsLiterals.TASK_TYPE: 'some_task_type'}
            try:
                runner_od.run(settings)
            except Exception:
                assert side_effect_passed


def get_mock_run():
    mock_run = _OfflineRun()
    mock_workspace = MagicMock()
    mock_run.experiment = MagicMock(return_value=Experiment(mock_workspace, "test", _create_in_cloud=False))
    return mock_run
