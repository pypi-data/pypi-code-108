import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from _pytest.monkeypatch import MonkeyPatch

import pytest

from PIL import Image

import torch

import azureml.automl.core.shared.constants as shared_constants

from azureml.data.dataset_factory import FileDatasetFactory

from azureml.automl.dnn.vision.common.utils import _get_default_device
from azureml.automl.dnn.vision.classification.common.transforms import _get_common_valid_transforms
from azureml.automl.dnn.vision.classification.inference.score import _featurize_with_model, _score_with_model
from azureml.automl.dnn.vision.classification.models import ModelFactory
from azureml.automl.dnn.vision.classification.common.classification_utils import _load_model_wrapper
from azureml.automl.dnn.vision.classification.common.constants import ModelLiterals, ModelParameters

from tests.common.run_mock import RunMock, ExperimentMock, WorkspaceMock, DatastoreMock

from azureml.automl.dnn.vision.common.artifacts_utils import save_model_checkpoint


@pytest.mark.usefixtures('new_clean_dir')
class TestInferenceModelWrapper:
    def setup(self):
        self.monkey_patch = MonkeyPatch()

    def test_inference_cpu(self, image_dir):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            model_name = 'seresnext'
            model_wrapper = ModelFactory().get_model_wrapper(model_name,
                                                             10,
                                                             multilabel=False,
                                                             device='cpu',
                                                             distributed=False,
                                                             rank=0)
            # save the model wrapper
            specs = {
                'multilabel': model_wrapper.multilabel,
                'model_settings': model_wrapper.model_settings,
                'labels': model_wrapper.labels
            }
            save_model_checkpoint(epoch=1,
                                  model_name=model_name,
                                  number_of_classes=model_wrapper.number_of_classes,
                                  specs=specs,
                                  model_state=model_wrapper.state_dict(),
                                  optimizer_state={},
                                  lr_scheduler_state={},
                                  output_dir=tmp_output_dir)

            model_file = os.path.join(tmp_output_dir, shared_constants.PT_MODEL_FILENAME)
            inference_model = _load_model_wrapper(model_file, False, 0, 'cpu')
            assert inference_model.labels == model_wrapper.labels
            assert inference_model.valid_resize_size == model_wrapper.valid_resize_size
            assert inference_model.valid_crop_size == model_wrapper.valid_crop_size

            image_path = os.path.join(image_dir, 'crack_1.jpg')
            im = Image.open(image_path)

            transforms_list = _get_common_valid_transforms(resize_to=model_wrapper.valid_resize_size,
                                                           crop_size=model_wrapper.valid_crop_size)
            tensor_image = torch.stack([transforms_list(im)], dim=0)
            outputs = inference_model.model(tensor_image)
            probs = inference_model.predict_probs_from_outputs(outputs)

            assert probs.shape[1] == model_wrapper.number_of_classes
            assert inference_model._featurizer(tensor_image).shape[0] == 1

    def test_featurization(self, root_dir, image_dir, src_image_list_file_name):
        image_class_list_file_path = os.path.join(root_dir, src_image_list_file_name)
        batch_size_list = range(1, 3)
        model_factory = ModelFactory()
        for model_name in model_factory._models_dict.keys():
            self._featurization_test(model_name, root_dir, image_dir, image_class_list_file_path, batch_size_list, 4)

    @staticmethod
    def _write_image_list_to_file(image_dir, image_class_list_file_path):
        Path(image_class_list_file_path).touch()
        with open(image_class_list_file_path, mode="w") as fp:
            for image_file in os.listdir(image_dir):
                fp.write(image_file + "\n")

    def test_featurization_invalid_image_file(self, root_dir, image_dir, image_list_file_name):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            temp_image_class_list_file_path = os.path.join(tmp_output_dir, image_list_file_name)
            self._write_image_list_to_file(image_dir, temp_image_class_list_file_path)
            expected_feature_file_length = 4  # Should not include invalid image.
            default_model_name = ModelFactory()._default_model
            self._featurization_test(default_model_name, root_dir, image_dir, temp_image_class_list_file_path, [3],
                                     expected_feature_file_length)
            self._featurization_test(default_model_name, root_dir, image_dir, temp_image_class_list_file_path, [1],
                                     expected_feature_file_length)

    @staticmethod
    def _featurization_test(model_name, root_dir, image_dir, image_class_list_file_path,
                            batch_size_list, expected_feature_file_length):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            device = _get_default_device()
            model_wrapper = ModelFactory().get_model_wrapper(model_name,
                                                             10,
                                                             multilabel=False,
                                                             device=device,
                                                             distributed=False,
                                                             rank=0)

            # run featurizations
            featurization_file = 'features.txt'
            features_output_file = os.path.join(tmp_output_dir, featurization_file)

            Path(features_output_file).touch()

            model_wrapper.transforms = _get_common_valid_transforms(
                resize_to=model_wrapper.valid_resize_size,
                crop_size=model_wrapper.valid_crop_size
            )

            for batch_size in batch_size_list:
                TestInferenceModelWrapper._featurization_batch_test(features_output_file, image_dir,
                                                                    image_class_list_file_path,
                                                                    model_wrapper, batch_size,
                                                                    expected_feature_file_length)

    @staticmethod
    def _featurization_batch_test(features_output_file, image_dir,
                                  image_class_list_file_path, inference_model_wrapper, batch_size,
                                  expected_feature_file_length):

        datastore_name = "TestDatastoreName"
        datastore_mock = DatastoreMock(datastore_name)
        workspace_mock = WorkspaceMock(datastore_mock)
        experiment_mock = ExperimentMock(workspace_mock)
        run_mock = RunMock(experiment_mock)

        _featurize_with_model(inference_model_wrapper, run_mock, root_dir=image_dir,
                              output_file=features_output_file,
                              image_list_file=image_class_list_file_path,
                              device=_get_default_device(),
                              batch_size=batch_size, num_workers=0)

        with open(features_output_file) as fp:
            for line in fp:
                obj = json.loads(line.strip())
                assert 'filename' in obj
                assert 'feature_vector' in obj
                assert len(obj['feature_vector']) > 0
        with open(features_output_file) as fp:
            lines = fp.readlines()
        assert len(lines) == expected_feature_file_length

    def test_score(self, root_dir, image_dir, src_image_list_file_name):
        image_class_list_file_path = os.path.join(root_dir, src_image_list_file_name)
        model_factory = ModelFactory()
        for model_name in model_factory._models_dict.keys():
            self._score_test(self.monkey_patch, model_name, root_dir, image_dir, image_class_list_file_path, 4, 10)

    def test_score_invalid_image_file(self, root_dir, image_dir, image_list_file_name):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            temp_image_class_list_file_path = os.path.join(tmp_output_dir, image_list_file_name)
            self._write_image_list_to_file(image_dir, temp_image_class_list_file_path)
            expected_score_file_length = 4  # Should not include invalid image.
            default_model_name = ModelFactory()._default_model
            self._score_test(self.monkey_patch, default_model_name, root_dir, image_dir,
                             temp_image_class_list_file_path, expected_score_file_length, 10)
            self._score_test(self.monkey_patch, default_model_name, root_dir, image_dir,
                             temp_image_class_list_file_path, expected_score_file_length, 1)

    @staticmethod
    def _score_test(monkey_patch, model_name, root_dir, image_dir, image_class_list_file_path,
                    expected_score_file_length, batch_size):

        with tempfile.TemporaryDirectory() as tmp_output_dir:
            device = _get_default_device()
            model_settings = {ModelLiterals.VALID_RESIZE_SIZE: ModelParameters.DEFAULT_VALID_RESIZE_SIZE,
                              ModelLiterals.VALID_CROP_SIZE: ModelParameters.DEFAULT_VALID_CROP_SIZE}
            model_wrapper = ModelFactory().get_model_wrapper(model_name,
                                                             10,
                                                             multilabel=False,
                                                             device=device,
                                                             distributed=False,
                                                             rank=0,
                                                             settings=model_settings)

            # run predictions
            predictions_file = 'predictions.txt'
            predictions_output_file = os.path.join(tmp_output_dir, predictions_file)

            datastore_name = "TestDatastoreName"
            datastore_mock = DatastoreMock(datastore_name)
            workspace_mock = WorkspaceMock(datastore_mock)
            experiment_mock = ExperimentMock(workspace_mock)
            run_mock = RunMock(experiment_mock)
            test_target_path = "TestTargetPath"
            labeled_dataset_file = os.path.join(tmp_output_dir, 'labeled_dataset.json')

            Path(predictions_output_file).touch()
            Path(labeled_dataset_file).touch()

            model_wrapper.transforms = _get_common_valid_transforms(
                resize_to=model_wrapper.valid_resize_size,
                crop_size=model_wrapper.valid_crop_size
            )

            def labeled_dataset_upload_mock(directory, data_path, overwrite):
                assert len(data_path) == 2
                assert data_path[0] == datastore_mock
                assert data_path[1] == test_target_path
                assert overwrite

                dir_files = os.listdir(directory)
                assert len(dir_files) == 1
                dir_file_0 = os.path.join(directory, dir_files[0])
                assert os.path.isfile(dir_file_0)

                with open(dir_file_0, "r") as f:
                    labeled_dataset_file_content = f.readlines()
                    assert len(labeled_dataset_file_content) == expected_score_file_length

                    for line in labeled_dataset_file_content:
                        line_contents = json.loads(line)
                        assert line_contents['image_url'].startswith('AmlDatastore://')
                        assert 'label' in line_contents
                        assert 'label_confidence' in line_contents

            with monkey_patch.context() as m:
                m.setattr(FileDatasetFactory, 'upload_directory', labeled_dataset_upload_mock)
                with patch("azureml.core.Dataset.Tabular.from_json_lines_files"):
                    _score_with_model(model_wrapper, run_mock, test_target_path,
                                      root_dir=image_dir,
                                      output_file=predictions_output_file,
                                      image_list_file=image_class_list_file_path,
                                      device=device,
                                      always_create_dataset=True,
                                      num_workers=0,
                                      labeled_dataset_file=labeled_dataset_file,
                                      batch_size=batch_size)

            with open(predictions_output_file) as fp:
                for line in fp:
                    obj = json.loads(line.strip())
                    assert 'filename' in obj
                    assert 'probs' in obj
                    assert len(obj['probs']) > 0
            with open(predictions_output_file) as fp:
                lines = fp.readlines()
            assert len(lines) == expected_score_file_length
