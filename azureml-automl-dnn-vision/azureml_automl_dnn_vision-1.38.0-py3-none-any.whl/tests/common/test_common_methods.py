# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for common methods."""
import argparse
import os
import pytest
import sys
import tempfile

import torch.utils.data as data

from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch
from _pytest.monkeypatch import MonkeyPatch

import azureml

from azureml.core import Run, Experiment
from azureml.automl.core.inference.inference import AutoMLInferenceArtifactIDs

from azureml.automl.dnn.vision.classification.runner import _parse_argument_settings as mc_parser
from azureml.automl.dnn.vision.object_detection.runner import _parse_argument_settings as od_parser
from azureml.automl.dnn.vision.object_detection_yolo.runner import _parse_argument_settings as od_yolo_parser

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.dataloaders import RobustDataLoader, _RobustCollateFn
from azureml.automl.dnn.vision.common.data_utils import validate_labels_files_paths
from azureml.automl.dnn.vision.common.utils import _merge_settings_args_defaults, _exception_handler, \
    _read_image, _pad, is_aml_dataset_input, _set_train_run_properties
from azureml.automl.dnn.vision.common.constants import SettingsLiterals, RunPropertyLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException, \
    AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.object_detection.common.constants import TilingLiterals

from azureml.data.dataset_factory import FileDatasetFactory

from .run_mock import RunMock, ExperimentMock, WorkspaceMock, DatastoreMock

_THIS_FILES_DIR = Path(os.path.dirname(__file__))
_PARENT_DIR = _THIS_FILES_DIR.parent
_VALID_PATH = "data/classification_data/multiclass.csv"
_INVALID_PATH = "invalid_path"


class MissingFilesDataset(data.Dataset):
    def __init__(self):
        self._labels = ['label_1', 'label_2', 'label_3']
        self._images = [1, None, 2]

    def __getitem__(self, index):
        return self._images[index], self._labels[index]

    def __len__(self):
        return len(self._labels)


class TestRobustDataLoader:
    def _test_data_loader(self, loader):
        all_data_len = 0
        for images, label in loader:
            all_data_len += images.shape[0]
        assert all_data_len == 2

    def _test_data_loader_with_exception_safe_iterator(self, loader):
        all_data_len = 0
        for images, label in utils._data_exception_safe_iterator(iter(loader)):
            all_data_len += images.shape[0]
        assert all_data_len == 2

    def test_robust_dataloader(self):
        dataset = MissingFilesDataset()
        dataloader = RobustDataLoader(dataset, batch_size=10, num_workers=0)
        self._test_data_loader(dataloader)
        self._test_data_loader_with_exception_safe_iterator(dataloader)

    def test_robust_dataloader_invalid_batch(self):
        dataset = MissingFilesDataset()
        dataloader = RobustDataLoader(dataset, batch_size=1, num_workers=0)
        with pytest.raises(AutoMLVisionDataException) as exc_info:
            self._test_data_loader(dataloader)
        assert exc_info.value.message == _RobustCollateFn.EMPTY_BATCH_ERROR_MESSAGE
        self._test_data_loader_with_exception_safe_iterator(dataloader)

        # Dataloader with multiple workers should raise the exception
        dataloader = RobustDataLoader(dataset, batch_size=1, num_workers=4)
        with pytest.raises(AutoMLVisionDataException) as exc_info:
            self._test_data_loader(dataloader)
        assert _RobustCollateFn.EMPTY_BATCH_ERROR_MESSAGE in exc_info.value.message
        self._test_data_loader_with_exception_safe_iterator(dataloader)


def test_config_merge():
    settings = {"a": "a_s", "b": 1, "c": "c_s"}

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--b')
    parser.add_argument('--d')
    parser.add_argument('--f')
    args = parser.parse_args(args=["--b", "b_a", "--d", "d_a", "--f", "f_a"])

    defaults = {"b": "b_d", "d": "d_d", "g": 10}

    merged_settings = _merge_settings_args_defaults(settings, vars(args), defaults)

    assert merged_settings["a"] == "a_s"
    assert merged_settings["b"] == 1
    assert merged_settings["c"] == "c_s"
    assert merged_settings["d"] == "d_a"
    assert merged_settings["f"] == "f_a"
    assert merged_settings["g"] == 10


@pytest.mark.parametrize(
    "passed_value,parsed_value",
    (["True", True],
     ["False", False],
     ["true", True],
     ["false", False],
     ["1", True],
     ["0", False]))
def test_boolean_args_parse(passed_value, parsed_value):
    args = ['early_stopping', 'nesterov', 'amsgrad']

    for arg in args:

        prefixed_arg = '--' + arg
        sys.argv = ['hd_image_classification_dnn_driver.py',
                    '--data-folder', '',
                    '--labels-file-root', '',
                    prefixed_arg, passed_value]

        settings, unknown = mc_parser(automl_settings={}, multilabel=False)
        assert settings[arg] == parsed_value
        assert not unknown

        settings, unknown = mc_parser(automl_settings={}, multilabel=True)
        assert settings[arg] == parsed_value
        assert not unknown

        settings, unknown = od_parser(automl_settings={})
        assert settings[arg] == parsed_value
        assert not unknown

        settings, unknown = od_yolo_parser(automl_settings={})
        assert settings[arg] == parsed_value
        assert not unknown

        sys.argv


def test_tmp_parser():
    # get model_name from argument SettingsLiterals.MODEL_NAME
    parser = argparse.ArgumentParser(allow_abbrev=False)
    utils.add_model_arguments(parser)
    input_mn = [f"--{SettingsLiterals.MODEL_NAME}", "model_a"]
    args_mn, _ = parser.parse_known_args(input_mn)
    args_dict_mn = utils.parse_model_conditional_space(vars(args_mn))
    model_name = args_dict_mn[SettingsLiterals.MODEL_NAME]
    assert model_name == "model_a"

    # get model_name from argument SettingsLiterals.MODEL
    input_m = [f"--{SettingsLiterals.MODEL}", f'{{"{SettingsLiterals.MODEL_NAME}": "model_b"}}']
    args_m, _ = parser.parse_known_args(input_m)
    args_dict_m = utils.parse_model_conditional_space(vars(args_m))
    model_name = args_dict_m[SettingsLiterals.MODEL_NAME]
    assert model_name == "model_b"


def test_labels_files_paths_val_not_aml_dataset_both_paths_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_both_paths_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_labels_valid_val_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_labels_invalid_val_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_labels_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH
    }

    validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_labels_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_val_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_val_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_with_no_paths():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: "",
        SettingsLiterals.LABELS_FILE: "",
        SettingsLiterals.VALIDATION_LABELS_FILE: ""
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)

    settings[SettingsLiterals.DATASET_ID] = ""

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)

    settings[SettingsLiterals.DATASET_ID] = None

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_aml_dataset_with_no_paths():
    settings = {
        SettingsLiterals.DATASET_ID: "some_dataset_id",
        SettingsLiterals.LABELS_FILE_ROOT: "",
        SettingsLiterals.LABELS_FILE: "",
        SettingsLiterals.VALIDATION_LABELS_FILE: ""
    }

    validate_labels_files_paths(settings)


def test_is_aml_dataset_input():
    assert not is_aml_dataset_input({})
    assert not is_aml_dataset_input({SettingsLiterals.DATASET_ID: ""})
    assert not is_aml_dataset_input({SettingsLiterals.DATASET_ID: None})
    assert is_aml_dataset_input({SettingsLiterals.DATASET_ID: "some_dataset_id"})


@mock.patch.object(azureml._restclient.JasmineClient, '__init__', lambda x, y, z, t, **kwargs: None)
@mock.patch.object(azureml._restclient.experiment_client.ExperimentClient, '__init__', lambda x, y, z, **kwargs: None)
@mock.patch('azureml._restclient.experiment_client.ExperimentClient', autospec=True)
@mock.patch('azureml._restclient.metrics_client.MetricsClient', autospec=True)
def test_exception_handler(mock_experiment_client, mock_metrics_client):
    mock_run = MagicMock(spec=Run)
    mock_workspace = MagicMock()
    mock_run.experiment = MagicMock(return_value=Experiment(mock_workspace, "test", _create_in_cloud=False))

    RANDOM_RUNTIME_ERROR = "random system error"
    DATA_RUNTIME_ERROR = "dataset issue"

    @_exception_handler
    def system_error_method(err):
        raise RuntimeError(err)

    @_exception_handler
    def user_error_method():
        raise AutoMLVisionDataException()

    @_exception_handler
    def shm_mem_error_method():
        raise Exception("This might be caused by insufficient shared memory")

    with patch.object(Run, 'get_context', return_value=mock_run):
        with pytest.raises(RuntimeError):
            system_error_method(RANDOM_RUNTIME_ERROR)
        mock_run.fail.assert_called_once()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'SystemError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'AutoMLVisionInternal'
        assert "Additional information: [Hidden as it may contain PII]" not in \
               mock_run.fail.call_args[1]['error_details'].message

        with pytest.raises(RuntimeError):
            system_error_method(DATA_RUNTIME_ERROR)
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'SystemError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'AutoMLVisionInternal'
        assert "Additional information: [Hidden as it may contain PII]" in \
               mock_run.fail.call_args[1]['error_details'].message

        with pytest.raises(AutoMLVisionDataException):
            user_error_method()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'UserError'

        with pytest.raises(Exception):
            shm_mem_error_method()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'UserError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'InvalidData'


@pytest.mark.parametrize('use_cv2', [False, True])
@pytest.mark.parametrize('image_url', ["../data/object_detection_data/images/invalid_image_file.jpg",
                                       "../data/object_detection_data/images/corrupt_image_file.png",
                                       "nonexistent_image_file.png",
                                       "../data/object_detection_data/images/000001679.png"])
def test_read_non_existing_image(use_cv2, image_url):
    image_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_url)
    img = _read_image(ignore_data_errors=True,
                      image_url=image_full_path,
                      use_cv2=use_cv2)
    if any(prefix in image_url for prefix in ['invalid', 'corrupt', 'nonexistent']):
        # PIL manages to load corrupt images
        if 'corrupt' in image_url and not use_cv2:
            return
        assert img is None, image_url
    else:
        assert img is not None, image_url


def test_pad():
    assert _pad([], 0) == []
    assert _pad([], 4) == []
    assert _pad([1], 0) == [1]
    assert _pad([1], 1) == [1]
    assert _pad([1], 4) == [1, 1, 1, 1]
    assert _pad([1, 1, 1, 1], 4) == [1, 1, 1, 1]
    assert _pad([1, 2, 3], 5) == [1, 2, 3, 1, 2]
    assert _pad([1, 2, 3, 4], 3) == [1, 2, 3, 4, 1, 2]


@mock.patch('azureml.automl.dnn.vision.common.utils._get_model_name')
def test_set_train_run_properties(mock_fun):
    ds_mock = DatastoreMock('some_ds')
    ws_mock = WorkspaceMock(ds_mock)
    exp_mock = ExperimentMock(ws_mock)
    run_mock = RunMock(exp_mock)
    model_name = "some_model_name"
    best_metric = 95
    _set_train_run_properties(run_mock, model_name, best_metric)

    run_properties = run_mock.properties

    mock_fun.assert_called_once_with(run_mock.id)
    assert run_properties['runTemplate'] == 'automl_child'
    assert run_properties['run_algorithm'] == model_name
    assert run_properties[RunPropertyLiterals.PIPELINE_SCORE] == best_metric
    assert run_properties[AutoMLInferenceArtifactIDs.ModelName] is not None
    assert AutoMLInferenceArtifactIDs.ModelName in run_properties


def test_round_numeric_values():
    assert utils.round_numeric_values({}, 3) == {}
    assert utils.round_numeric_values({"a": 1.11111}, 2)["a"] == 1.11
    assert utils.round_numeric_values({"a": 1.11111}, 3)["a"] == 1.111
    assert utils.round_numeric_values({"a": 1.11111}, 4)["a"] == 1.1111

    res_dict = utils.round_numeric_values({"a": 1.11111, "b": "val"}, 4)
    assert res_dict["a"] == 1.1111
    assert res_dict["b"] == "val"

    res_dict = utils.round_numeric_values({"a": "a", "b": "b"}, 1)
    assert res_dict["a"] == "a"
    assert res_dict["b"] == "b"


def test_fix_tiling_settings_in_args_dict():
    # tile_grid_size not present in args_dict
    args_dict = {}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert TilingLiterals.TILE_GRID_SIZE not in args_dict

    # tile_grid_size present in args_dict, but None
    args_dict = {TilingLiterals.TILE_GRID_SIZE: None}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] is None

    # tile_grid_size present in args_dict and is a tuple
    args_dict = {TilingLiterals.TILE_GRID_SIZE: (3, 2)}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)

    # tile_grid_size present in args_dict and is a string
    args_dict = {TilingLiterals.TILE_GRID_SIZE: "(3, 2)"}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)


class TestAmlDatasetHelper():
    def setup(self):
        self.monkey_patch = MonkeyPatch()

    def test_labeled_dataset_create_file_upload_path(self):
        datastore_name = "TestDatastoreName"
        datastore_mock = DatastoreMock(datastore_name)
        workspace_mock = WorkspaceMock(datastore_mock)
        experiment_mock = ExperimentMock(workspace_mock)
        run_mock = RunMock(experiment_mock)

        test_target_path = "TestTargetPath"
        labeled_dataset_file_name = "labeled_dataset.json"

        def _test_file_upload_path(monkey_patch, labeled_dataset_file):
            Path(labeled_dataset_file).touch()

            def _upload_directory_mock(directory, data_path, overwrite):
                assert len(data_path) == 2
                assert data_path[0] == datastore_mock
                assert data_path[1] == test_target_path
                assert overwrite

                # Check that labeled_dataset_file is copied at root of directory
                dir_files = os.listdir(directory)
                assert len(dir_files) == 1
                file_0_path = os.path.join(directory, dir_files[0])
                assert os.path.isfile(file_0_path)
                assert dir_files[0] == os.path.basename(labeled_dataset_file)

            with monkey_patch.context() as m:
                m.setattr(FileDatasetFactory, "upload_directory", _upload_directory_mock)
                with patch("azureml.core.Dataset.Tabular.from_json_lines_files"):
                    AmlDatasetHelper.create(run_mock, datastore_mock, labeled_dataset_file,
                                            test_target_path, "TestTask")

        with tempfile.TemporaryDirectory() as tmp_output_dir:
            labeled_dataset_file = os.path.join(tmp_output_dir, labeled_dataset_file_name)
            _test_file_upload_path(self.monkey_patch, labeled_dataset_file)

            dir_path = os.path.join(tmp_output_dir, "dir1", "dir2")
            labeled_dataset_file = os.path.join(dir_path, labeled_dataset_file_name)
            os.makedirs(dir_path, exist_ok=True)
            _test_file_upload_path(self.monkey_patch, labeled_dataset_file)

            try:
                _test_file_upload_path(self.monkey_patch, labeled_dataset_file_name)
            finally:
                os.remove(labeled_dataset_file_name)
