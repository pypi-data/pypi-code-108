import json
import os
import pytest
import tempfile
import torch
import torchvision.transforms.functional as functional

from unittest.mock import patch
from _pytest.monkeypatch import MonkeyPatch

from azureml.data.dataset_factory import FileDatasetFactory

from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.utils import get_model_layer_info
from azureml.automl.dnn.vision.object_detection.common.boundingbox import BoundingBox
from azureml.automl.dnn.vision.object_detection.common.constants import training_settings_defaults, \
    ModelNames
from azureml.automl.dnn.vision.object_detection.writers.score import _score_with_model
from azureml.automl.dnn.vision.object_detection.models.detection import setup_model
from azureml.automl.dnn.vision.object_detection.models.object_detection_model_wrappers \
    import FasterRCNNResnet50FPNWrapper, RetinaNetResnet50FPNWrapper, FasterRCNNModelSettings, \
    RetinaNetModelSettings, ObjectDetectionModelFactory
from azureml.automl.dnn.vision.object_detection.models.instance_segmentation_model_wrappers \
    import MaskRCNNResnet50FPNWrapper, InstanceSegmentationModelFactory
from pathlib import Path
from PIL import Image

from .utils import CocoBaseModelWrapper
from ..common.run_mock import RunMock, ExperimentMock, WorkspaceMock, DatastoreMock
from ..common.utils import check_exported_onnx_od_model, delete_model_weights


@pytest.mark.usefixtures('new_clean_dir')
class TestModelWrappers:
    def setup(self):
        self.monkey_patch = MonkeyPatch()

    def test_inference_base_model_wrapper(self, data_root):
        model_wrapper = CocoBaseModelWrapper()
        # TODO: Both of the following lines should be removed once this moves to initialization
        model_wrapper.classes = ['A'] * 91
        model_wrapper.to_device('cpu')
        im = Image.open(os.path.join(data_root, 'coco_classes_image.jpg'))
        bounding_boxes = model_wrapper.predict([im, im])
        assert len(bounding_boxes) == 2

        for box in bounding_boxes[0]:
            assert isinstance(box, BoundingBox)
            assert box.label == 'A'

    def test_all_models_have_model_layer_info(self):
        model_factory = ObjectDetectionModelFactory()
        is_model_factory = InstanceSegmentationModelFactory()

        model_names = list(model_factory._models_dict.keys()) + \
            list(is_model_factory._models_dict.keys()) + [ModelNames.YOLO_V5]
        for model_name in model_names:
            # Should not raise an error if we defined the model layer info.
            get_model_layer_info(model_name)

        with pytest.raises(AutoMLVisionSystemException):
            get_model_layer_info("nonexistent_model")

    def test_wrappers_export_onnx(self, data_root):
        # right now only initialization and making sure that the model is working
        device = training_settings_defaults[SettingsLiterals.DEVICE]
        image = Image.open(os.path.join(data_root, 'coco_classes_image.jpg')).convert('RGB')
        image_tensor = functional.to_tensor(image).unsqueeze(0).to(device=device)
        resized_image = torch.nn.functional.interpolate(image_tensor, size=(600, 800),
                                                        mode='bilinear', align_corners=False)

        def get_model_output(wrapper, input, device):
            wrapper.to_device(device=device)
            wrapper.model.eval()
            return wrapper.model(input)

        number_of_classes = 10
        # Inference with onnx model fails in torch 1.7.1 as box_score_thresh is interpreted as float64 and
        # float64 is not supported in one of the nodes(Greater). Explicitly passing it here so that
        # FasterRCNNResnet50FPNWrapper takes care of converting it to float tensor to solve the issue.
        r50_settings = FasterRCNNModelSettings(settings={"box_score_thresh": 0.05})
        r50 = FasterRCNNResnet50FPNWrapper(number_of_classes=number_of_classes, model_settings=r50_settings)
        r50_file = 'FasterRCNNResnet50FPNWrapper.onnx'
        r50.export_onnx_model(file_path=r50_file, device=device)
        check_exported_onnx_od_model(r50_file, r50, resized_image, device, get_model_output, number_of_classes)

        # export onnx w/ normalization
        r50n_file = 'FasterRCNNResnet50FPNWrapperNorm.onnx'
        r50.export_onnx_model(file_path=r50n_file, device=device, enable_norm=True)
        check_exported_onnx_od_model(r50n_file, r50, resized_image, device, get_model_output, number_of_classes,
                                     is_norm=True)

        m50 = MaskRCNNResnet50FPNWrapper(number_of_classes=number_of_classes, model_settings=r50_settings)
        m50_file = 'MaskRCNNResnet50FPNWrapper.onnx'
        m50.export_onnx_model(file_path=m50_file, device=device)
        check_exported_onnx_od_model(m50_file, m50, resized_image, device, get_model_output, number_of_classes)

        retinanet50_settings = RetinaNetModelSettings(settings={"box_score_thresh": 0.05})
        retinanet50 = RetinaNetResnet50FPNWrapper(number_of_classes=number_of_classes,
                                                  model_settings=retinanet50_settings)
        retinanet50_file = 'RetinaNetResnet50FPNWrapper.onnx'
        retinanet50.export_onnx_model(file_path=retinanet50_file, device=device)
        check_exported_onnx_od_model(retinanet50_file, retinanet50, resized_image, device, get_model_output,
                                     number_of_classes)

        # delete model weights which are in predefined place
        delete_model_weights()

    def test_score(self, data_root, image_list_file_name):
        image_dir = os.path.join(data_root, 'images')
        image_od_list_file_path = os.path.join(data_root, image_list_file_name)
        with open(image_od_list_file_path) as fp:
            expected_score_file_length = len(fp.readlines())

        model_factory = ObjectDetectionModelFactory()
        for model_name in model_factory._models_dict.keys():
            # batch_size 1
            self._scoring_test(self.monkey_patch, model_name, image_dir, image_od_list_file_path, 1,
                               expected_score_file_length)
            # batch_size 2
            self._scoring_test(self.monkey_patch, model_name, image_dir, image_od_list_file_path, 2,
                               expected_score_file_length)

    def test_score_invalid_image_file(self, data_root, image_list_file_name):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            image_dir = os.path.join(data_root, 'images')
            temp_image_od_list_file_path = os.path.join(tmp_output_dir, image_list_file_name)
            # copy list from src_image_od_list_file.txt and add one extra file.
            image_od_list_file_path = os.path.join(data_root, image_list_file_name)
            with open(image_od_list_file_path) as input_fp:
                lines = input_fp.readlines()
                with open(temp_image_od_list_file_path, 'w') as fp:
                    fp.writelines(lines)
                    fp.write("\n")
                    fp.write("invalid_image_file.jpg" + "\n")

            with open(temp_image_od_list_file_path) as fp:
                expected_score_file_length = len(fp.readlines()) - 1  # One invalid image file in the images folder.

            default_model_name = ObjectDetectionModelFactory()._default_model
            self._scoring_test(self.monkey_patch, default_model_name, image_dir, temp_image_od_list_file_path, 1,
                               expected_score_file_length)
            self._scoring_test(self.monkey_patch, default_model_name, image_dir, temp_image_od_list_file_path, 3,
                               expected_score_file_length)

    @staticmethod
    def _scoring_test(monkey_patch, model_name, image_dir, image_od_list_file_path, batch_size,
                      expected_score_file_length):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Pass number_of_classes as None so that all layers in the model have pretrained weights
            # and there are some predictions.
            model_wrapper = setup_model(model_name, number_of_classes=None, classes=['A'] * 91, device='cpu')

            # run predictions
            predictions_file = 'predictions_od.txt'
            predictions_output_file = os.path.join(tmp_output_dir, predictions_file)

            datastore_name = "TestDatastoreName"
            datastore_mock = DatastoreMock(datastore_name)
            workspace_mock = WorkspaceMock(datastore_mock)
            experiment_mock = ExperimentMock(workspace_mock)
            run_mock = RunMock(experiment_mock)
            test_target_path = "TestTargetPath"
            labeled_dataset_file = os.path.join(tmp_output_dir, "labeled_dataset.json")

            Path(predictions_output_file).touch()
            Path(labeled_dataset_file).touch()

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
                                      root_dir=image_dir, output_file=predictions_output_file,
                                      image_list_file=image_od_list_file_path,
                                      device='cpu', batch_size=batch_size,
                                      always_create_dataset=True,
                                      num_workers=0,
                                      labeled_dataset_file=labeled_dataset_file)

            with open(predictions_output_file) as fp:
                for line in fp:
                    obj = json.loads(line.strip())
                    assert 'filename' in obj
                    assert 'boxes' in obj
                    assert len(obj['boxes']) > 0
                    assert 'box' in obj['boxes'][0]
                    assert 'label' in obj['boxes'][0]
                    assert 'score' in obj['boxes'][0]
            with open(predictions_output_file) as fp:
                lines = fp.readlines()
            assert len(lines) == expected_score_file_length

            # expected_path = test_target_path + "/labeled_dataset.json"
