import os
import pytest
import torch
import torchvision.transforms.functional as functional

from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.automl.dnn.vision.object_detection.common.constants import training_settings_defaults
from azureml.automl.dnn.vision.object_detection.models.object_detection_model_wrappers \
    import FasterRCNNModelSettings, FasterRCNNResnet18FPNWrapper
from azureml.automl.dnn.vision.object_detection.models.instance_segmentation_model_wrappers \
    import MaskRCNNResnet18FPNWrapper
from PIL import Image

from ..common.utils import check_exported_onnx_od_model, delete_model_weights


@pytest.mark.usefixtures('new_clean_dir')
class TestSecondaryFasterrcnnModelWrappers:
    def test_secondary_fasterrcnn_wrappers_export_onnx(self, data_root):
        device = training_settings_defaults[SettingsLiterals.DEVICE]
        image = Image.open(os.path.join(data_root, 'coco_classes_image.jpg')).convert('RGB')
        image_tensor = functional.to_tensor(image).unsqueeze(0).to(device=device)
        resized_image = torch.nn.functional.interpolate(image_tensor, size=(600, 800),
                                                        mode='bilinear', align_corners=False)
        number_of_classes = 10
        fasterrcnn_settings = FasterRCNNModelSettings(settings={"box_score_thresh": 0.05})

        def get_model_output(wrapper, input, device):
            wrapper.to_device(device=device)
            wrapper.model.eval()
            return wrapper.model(input)

        r18 = FasterRCNNResnet18FPNWrapper(number_of_classes=number_of_classes, model_settings=fasterrcnn_settings)
        r18_file = 'FasterRCNNResnet18FPNWrapper.onnx'
        r18.export_onnx_model(file_path=r18_file, device=device)
        check_exported_onnx_od_model(r18_file, r18, resized_image, device, get_model_output, number_of_classes)

        # commenting these large models for now since the program is killed due to RAM OOM
        '''
        r34 = FasterRCNNResnet34FPNWrapper(number_of_classes=number_of_classes, model_settings=fasterrcnn_settings)
        r34_file = 'FasterRCNNResnet34FPNWrapper.onnx'
        r34.export_onnx_model(file_path=r34_file, device=device)
        check_exported_onnx_od_model(r34_file, r34, resized_image, device, get_model_output, number_of_classes)

        r101 = FasterRCNNResnet101FPNWrapper(number_of_classes=number_of_classes, model_settings=fasterrcnn_settings)
        r101_file = 'FasterRCNNResnet101FPNWrapper.onnx'
        r101.export_onnx_model(file_path=r101_file, device=device)
        check_exported_onnx_od_model(r101_file, r101, resized_image, device, get_model_output, number_of_classes)

        r152 = FasterRCNNResnet152FPNWrapper(number_of_classes=number_of_classes, model_settings=fasterrcnn_settings)
        r152_file = 'FasterRCNNResnet152FPNWrapper.onnx'
        r152.export_onnx_model(file_path=r152_file, device=device)
        check_exported_onnx_od_model(r152_file, r152, resized_image, device, get_model_output, number_of_classes)
        '''
        # delete model weights which are in predefined place
        delete_model_weights()

    def test_secondary_maskrcnn_wrappers_export_onnx(self, data_root):
        device = training_settings_defaults[SettingsLiterals.DEVICE]
        image = Image.open(os.path.join(data_root, 'coco_classes_image.jpg')).convert('RGB')
        image_tensor = functional.to_tensor(image).unsqueeze(0).to(device=device)
        resized_image = torch.nn.functional.interpolate(image_tensor, size=(600, 800),
                                                        mode='bilinear', align_corners=False)
        number_of_classes = 10
        maskrcnn_settings = FasterRCNNModelSettings(settings={"box_score_thresh": 0.05})

        def get_model_output(wrapper, input, device):
            wrapper.to_device(device=device)
            wrapper.model.eval()
            return wrapper.model(input)

        m18 = MaskRCNNResnet18FPNWrapper(number_of_classes=number_of_classes, model_settings=maskrcnn_settings)
        m18_file = 'MaskRCNNResnet18FPNWrapper.onnx'
        m18.export_onnx_model(file_path=m18_file, device=device)
        check_exported_onnx_od_model(m18_file, m18, resized_image, device, get_model_output, number_of_classes)

        # commenting these large models for now since the program is killed due to RAM OOM
        '''
        m34 = MaskRCNNResnet34FPNWrapper(number_of_classes=number_of_classes, model_settings=maskrcnn_settings)
        m34_file = 'MaskRCNNResnet34FPNWrapper.onnx'
        m34.export_onnx_model(file_path=m34_file, device=device)
        check_exported_onnx_od_model(m34_file, m34, resized_image, device, get_model_output, number_of_classes)

        m101 = MaskRCNNResnet101FPNWrapper(number_of_classes=number_of_classes, model_settings=maskrcnn_settings)
        m101_file = 'MaskRCNNResnet101FPNWrapper.onnx'
        m101.export_onnx_model(file_path=m101_file, device=device)
        check_exported_onnx_od_model(m101_file, m101, resized_image, device, get_model_output, number_of_classes)

        m152 = MaskRCNNResnet152FPNWrapper(number_of_classes=number_of_classes, model_settings=maskrcnn_settings)
        m152_file = 'MaskRCNNResnet152FPNWrapper.onnx'
        m152.export_onnx_model(file_path=m152_file, device=device)
        check_exported_onnx_od_model(m152_file, m152, resized_image, device, get_model_output, number_of_classes)
        '''
        # delete model weights which are in predefined place
        delete_model_weights()
