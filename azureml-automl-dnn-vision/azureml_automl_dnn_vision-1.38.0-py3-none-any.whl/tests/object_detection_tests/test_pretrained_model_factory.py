import pytest
import torch

from azureml.automl.dnn.vision.common.constants import PretrainedModelNames, PretrainedModelUrls
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory

from ..common.utils import delete_model_weights


@pytest.mark.usefixtures('new_clean_dir')
def test_get_pretrained_models():
    mdl = PretrainedModelFactory.fasterrcnn_resnet18_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.fasterrcnn_resnet34_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.fasterrcnn_resnet50_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.fasterrcnn_resnet101_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.fasterrcnn_resnet152_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.retinanet_restnet50_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.resnet_fpn_backbone(PretrainedModelNames.RESNET18, pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.maskrcnn_resnet18_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.maskrcnn_resnet34_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.maskrcnn_resnet50_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.maskrcnn_resnet101_fpn(pretrained=True)
    assert mdl is not None
    mdl = PretrainedModelFactory.maskrcnn_resnet152_fpn(pretrained=True)
    assert mdl is not None

    # delete model weights which are in predefined place
    delete_model_weights()


@pytest.mark.usefixtures('new_clean_dir')
def test_get_pretrained_models_yolo():
    ckpt = PretrainedModelFactory._load_state_dict_from_url_with_retry(
        PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.YOLOV5_SMALL], map_location=torch.device("cpu"))
    assert ckpt is not None
    ckpt = PretrainedModelFactory._load_state_dict_from_url_with_retry(
        PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.YOLOV5_MEDIUM], map_location=torch.device("cpu"))
    assert ckpt is not None
    ckpt = PretrainedModelFactory._load_state_dict_from_url_with_retry(
        PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.YOLOV5_LARGE], map_location=torch.device("cpu"))
    assert ckpt is not None
    ckpt = PretrainedModelFactory._load_state_dict_from_url_with_retry(
        PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.YOLOV5_XLARGE], map_location=torch.device("cpu"))
    assert ckpt is not None

    # delete model weights which are in predefined place
    delete_model_weights()
