import pytest
import tempfile

from azureml.train.automl import constants
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.vision.common.constants import SettingsLiterals, \
    TrainingLiterals as CommonTrainingLiterals
from azureml.core import Experiment
from azureml.core.run import Run

image_folder = 'object_detection_data/images'
labels_file = 'object_detection_data/train_annotations.json'
mock_dataset = None


def _get_settings(tmp_output_dir, add_validation_dataset=True, use_aml_dataset=True):
    settings = {SettingsLiterals.OUTPUT_DIR: tmp_output_dir,
                SettingsLiterals.TASK_TYPE: constants.Tasks.IMAGE_OBJECT_DETECTION,
                CommonTrainingLiterals.NUMBER_OF_EPOCHS: 1}
    if use_aml_dataset:
        from .test_datasets import TestAmlDatasetObjectDetectionWrapper
        mockworkspace, test_dataset_id, test_files_full_path, test_labels = \
            TestAmlDatasetObjectDetectionWrapper._build_dataset()
        settings[SettingsLiterals.DATASET_ID] = test_dataset_id
        global mock_dataset
        mock_dataset = mockworkspace._ds
        if add_validation_dataset:
            settings[SettingsLiterals.VALIDATION_DATASET_ID] = test_dataset_id
    else:
        settings[SettingsLiterals.IMAGE_FOLDER] = image_folder
        settings[SettingsLiterals.LABELS_FILE] = labels_file
        if add_validation_dataset:
            settings[SettingsLiterals.VALIDATION_LABELS_FILE] = labels_file
    return settings


@pytest.mark.usefixtures('new_clean_dir')
@patch("azureml.automl.core.shared._diagnostics.contract.Contract.assert_type")
@patch('azureml.core.Dataset')
@patch('azureml.automl.dnn.vision.object_detection.data.datasets.augmentations_transform')
@pytest.mark.parametrize('add_validation_dataset', [True, False])
@pytest.mark.parametrize('use_aml_dataset', [False])  # TODO: change to [True, False] when figuring out the mocking
def test_use_transform_local_run(assert_type_mock, mock_dataset_class, mock_transform,
                                 add_validation_dataset, use_aml_dataset):
    """Tests that we successfully replace the transform function in the model."""
    assert_type_mock.return_value = None

    mock_run = MagicMock()
    mock_workspace = MagicMock()
    mock_run.experiment = MagicMock(return_value=Experiment(mock_workspace, "test", _create_in_cloud=False))

    mock_dataset_class._properties = {}
    mock_dataset_class.get_by_id = lambda ws, dataset_id: mock_dataset

    with patch.object(Run, 'get_context', return_value=mock_run):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            settings = _get_settings(tmp_output_dir, add_validation_dataset, use_aml_dataset)

            # the import has to be here to mock Dataset class before it gets imported
            from azureml.automl.dnn.vision.object_detection import runner
            try:
                runner.run(settings)
            except Exception:
                pass

            assert mock_transform.called
            assert mock_transform.call_args is not None
            assert mock_transform.call_args.args[-1] is not None
