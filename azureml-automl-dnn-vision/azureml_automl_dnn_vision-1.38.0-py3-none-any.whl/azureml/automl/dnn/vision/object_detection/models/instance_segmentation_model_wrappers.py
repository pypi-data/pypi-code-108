# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper function to build instance segmentation wrappers."""

import abc
from typing import Optional

from azureml.automl.dnn.vision.object_detection.models.object_detection_model_wrappers import \
    FasterRCNNResnetFPNWrapper, FasterRCNNModelSettings, ObjectDetectionModelFactory, \
    convert_box_score_thresh_to_float_tensor
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

from ..common.constants import ModelNames, MaskRCNNLiterals, MaskRCNNParameters, ModelLiterals
from ...common.constants import ArtifactLiterals, PretrainedModelNames
from ...common.pretrained_model_utilities import PretrainedModelFactory
from ...common.logging_utils import get_logger

logger = get_logger(__name__)


class MaskRCNNResnetFPNWrapper(FasterRCNNResnetFPNWrapper, abc.ABC):
    """Abstract model wrapper for Mask RCNN with Resnet FPN backbone."""

    def __init__(self, model_name, number_of_classes=None, model_state=None, specs=None,
                 model_settings=None, inference_settings=None):
        """
        :param model_name: Name of the resnet model to use as a backbone
        :type model_name: str
        :param number_of_classes: Number of object classes
        :type number_of_classes: int
        :param model_state: Model weights. If None, then a new model is created
        :type model_state: dict
        :param specs: specifications for creating the model
        :type specs: dict
        :param model_settings: Optional argument to define model settings
        :type model_settings: BaseModelSettings
        :param inference_settings: Optional argument to define inference settings to use with this model
        :type inference_settings: Optional[Dict[str, Any]]
        """
        super().__init__(model_name=model_name, number_of_classes=number_of_classes,
                         model_state=model_state, specs=specs, model_settings=model_settings,
                         inference_settings=inference_settings)

    def _create_model(self, number_of_classes, specs=None, load_pretrained_model_dict=True):
        if specs is None:
            specs = {}

        kwargs = {} if self.model_settings is None else self.model_settings.model_init_kwargs()
        kwargs = convert_box_score_thresh_to_float_tensor(ModelLiterals.BOX_SCORE_THRESH, **kwargs)

        model = self._model_constructor(pretrained=True,
                                        load_pretrained_model_dict=load_pretrained_model_dict,
                                        **kwargs)

        if number_of_classes is not None:
            input_features_box = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(input_features_box,
                                                              number_of_classes)

            input_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
            hidden_layer = specs.get(MaskRCNNLiterals.MASK_PREDICTOR_HIDDEN_DIM,
                                     MaskRCNNParameters.DEFAULT_MASK_PREDICTOR_HIDDEN_DIM)
            model.roi_heads.mask_predictor = MaskRCNNPredictor(input_features_mask,
                                                               hidden_layer,
                                                               number_of_classes)

        return model

    def export_onnx_model(self, file_path: str = ArtifactLiterals.ONNX_MODEL_FILE_NAME, device: Optional[str] = None,
                          enable_norm: bool = False) -> None:
        """
        Export the pytorch model to onnx model file.

        :param file_path: file path to save the exported onnx model.
        :type file_path: str
        :param device: device where model should be run (usually 'cpu' or 'cuda:0' if it is the first gpu)
        :type device: str
        :param enable_norm: enable normalization when exporting onnx
        :type enable_norm: bool
        """
        self._export_onnx_model_with_names(file_path, device, enable_norm,
                                           input_names=['input'],
                                           output_names=['boxes', 'labels', 'scores', 'masks'],
                                           dynamic_axes={'input': {0: 'batch', 1: 'channel', 2: 'height', 3: 'width'},
                                                         'boxes': {0: 'prediction'},
                                                         'labels': {0: 'prediction'},
                                                         'scores': {0: 'prediction'},
                                                         'masks': {0: 'prediction',
                                                                   2: 'height',
                                                                   3: 'width'}})


class MaskRCNNResnet18FPNWrapper(MaskRCNNResnetFPNWrapper):
    """Model wrapper for Mask RCNN with Resnet18 FPN backbone."""

    def __init__(self, number_of_classes=None, model_state=None, specs=None,
                 model_settings=None, inference_settings=None):
        """
        :param number_of_classes: Number of object classes
        :type number_of_classes: int
        :param model_state: Model weights. If None, then a new model is created
        :type model_state: dict
        :param specs: specifications for creating the model
        :type specs: dict
        :param model_settings: Optional argument to define model settings
        :type model_settings: BaseModelSettings
        :param inference_settings: Optional argument to define inference settings to use with this model
        :type inference_settings: Optional[Dict[str, Any]]
        """
        super().__init__(model_name=ModelNames.MASK_RCNN_RESNET18_FPN,
                         number_of_classes=number_of_classes,
                         model_state=model_state, specs=specs, model_settings=model_settings,
                         inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.maskrcnn_resnet18_fpn(pretrained=pretrained,
                                                            load_pretrained_model_dict=load_pretrained_model_dict,
                                                            **kwargs)


class MaskRCNNResnet34FPNWrapper(MaskRCNNResnetFPNWrapper):
    """Model wrapper for Mask RCNN with Resnet34 FPN backbone."""

    def __init__(self, number_of_classes=None, model_state=None, specs=None,
                 model_settings=None, inference_settings=None):
        """
        :param number_of_classes: Number of object classes
        :type number_of_classes: int
        :param model_state: Model weights. If None, then a new model is created
        :type model_state: dict
        :param specs: specifications for creating the model
        :type specs: dict
        :param model_settings: Optional argument to define model settings
        :type model_settings: BaseModelSettings
        :param inference_settings: Optional argument to define inference settings to use with this model
        :type inference_settings: Optional[Dict[str, Any]]
        """
        super().__init__(model_name=ModelNames.MASK_RCNN_RESNET34_FPN,
                         number_of_classes=number_of_classes,
                         model_state=model_state, specs=specs, model_settings=model_settings,
                         inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.maskrcnn_resnet34_fpn(pretrained=pretrained,
                                                            load_pretrained_model_dict=load_pretrained_model_dict,
                                                            **kwargs)


class MaskRCNNResnet50FPNWrapper(MaskRCNNResnetFPNWrapper):
    """Model wrapper for Mask RCNN with Resnet50 FPN backbone."""

    def __init__(self, number_of_classes=None, model_state=None, specs=None,
                 model_settings=None, inference_settings=None):
        """
        :param number_of_classes: Number of object classes
        :type number_of_classes: int
        :param model_state: Model weights. If None, then a new model is created
        :type model_state: dict
        :param specs: specifications for creating the model
        :type specs: dict
        :param model_settings: Optional argument to define model settings
        :type model_settings: BaseModelSettings
        :param inference_settings: Optional argument to define inference settings to use with this model
        :type inference_settings: Optional[Dict[str, Any]]
        """
        super().__init__(model_name=ModelNames.MASK_RCNN_RESNET50_FPN,
                         number_of_classes=number_of_classes,
                         model_state=model_state, specs=specs, model_settings=model_settings,
                         inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.maskrcnn_resnet50_fpn(pretrained=pretrained,
                                                            load_pretrained_model_dict=load_pretrained_model_dict,
                                                            **kwargs)


class MaskRCNNResnet101FPNWrapper(MaskRCNNResnetFPNWrapper):
    """Model wrapper for Mask RCNN with Resnet101 FPN backbone."""

    def __init__(self, number_of_classes=None, model_state=None, specs=None,
                 model_settings=None, inference_settings=None):
        """
        :param number_of_classes: Number of object classes
        :type number_of_classes: int
        :param model_state: Model weights. If None, then a new model is created
        :type model_state: dict
        :param specs: specifications for creating the model
        :type specs: dict
        :param model_settings: Optional argument to define model settings
        :type model_settings: BaseModelSettings
        :param inference_settings: Optional argument to define inference settings to use with this model
        :type inference_settings: Optional[Dict[str, Any]]
        """
        super().__init__(model_name=ModelNames.MASK_RCNN_RESNET101_FPN,
                         number_of_classes=number_of_classes,
                         model_state=model_state, specs=specs, model_settings=model_settings,
                         inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.maskrcnn_resnet101_fpn(pretrained=pretrained,
                                                             load_pretrained_model_dict=load_pretrained_model_dict,
                                                             **kwargs)


class MaskRCNNResnet152FPNWrapper(MaskRCNNResnetFPNWrapper):
    """Model wrapper for Mask RCNN with Resnet152 FPN backbone."""

    def __init__(self, number_of_classes=None, model_state=None, specs=None,
                 model_settings=None, inference_settings=None):
        """
        :param number_of_classes: Number of object classes
        :type number_of_classes: int
        :param model_state: Model weights. If None, then a new model is created
        :type model_state: dict
        :param specs: specifications for creating the model
        :type specs: dict
        :param model_settings: Optional argument to define model settings
        :type model_settings: BaseModelSettings
        :param inference_settings: Optional argument to define inference settings to use with this model
        :type inference_settings: Optional[Dict[str, Any]]
        """
        super().__init__(model_name=ModelNames.MASK_RCNN_RESNET152_FPN,
                         number_of_classes=number_of_classes,
                         model_state=model_state, specs=specs, model_settings=model_settings,
                         inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.maskrcnn_resnet152_fpn(pretrained=pretrained,
                                                             load_pretrained_model_dict=load_pretrained_model_dict,
                                                             **kwargs)


class InstanceSegmentationModelFactory(ObjectDetectionModelFactory):
    """Factory function to create mask rcnn models."""

    def __init__(self) -> None:
        """Init method."""
        super().__init__()

        self._models_dict = {
            ModelNames.MASK_RCNN_RESNET18_FPN: MaskRCNNResnet18FPNWrapper,
            ModelNames.MASK_RCNN_RESNET34_FPN: MaskRCNNResnet34FPNWrapper,
            ModelNames.MASK_RCNN_RESNET50_FPN: MaskRCNNResnet50FPNWrapper,
            ModelNames.MASK_RCNN_RESNET101_FPN: MaskRCNNResnet101FPNWrapper,
            ModelNames.MASK_RCNN_RESNET152_FPN: MaskRCNNResnet152FPNWrapper
        }
        self._pre_trained_model_names_dict = {
            ModelNames.MASK_RCNN_RESNET18_FPN: PretrainedModelNames.MASKRCNN_RESNET18_FPN_COCO,
            ModelNames.MASK_RCNN_RESNET34_FPN: PretrainedModelNames.MASKRCNN_RESNET34_FPN_COCO,
            ModelNames.MASK_RCNN_RESNET50_FPN: PretrainedModelNames.MASKRCNN_RESNET50_FPN_COCO,
            ModelNames.MASK_RCNN_RESNET101_FPN: PretrainedModelNames.MASKRCNN_RESNET101_FPN_COCO,
            ModelNames.MASK_RCNN_RESNET152_FPN: PretrainedModelNames.MASKRCNN_RESNET152_FPN_COCO
        }
        self._model_settings_dict = {
            ModelNames.MASK_RCNN_RESNET18_FPN: FasterRCNNModelSettings,
            ModelNames.MASK_RCNN_RESNET34_FPN: FasterRCNNModelSettings,
            ModelNames.MASK_RCNN_RESNET50_FPN: FasterRCNNModelSettings,
            ModelNames.MASK_RCNN_RESNET101_FPN: FasterRCNNModelSettings,
            ModelNames.MASK_RCNN_RESNET152_FPN: FasterRCNNModelSettings
        }
        self._default_model = ModelNames.MASK_RCNN_RESNET50_FPN
