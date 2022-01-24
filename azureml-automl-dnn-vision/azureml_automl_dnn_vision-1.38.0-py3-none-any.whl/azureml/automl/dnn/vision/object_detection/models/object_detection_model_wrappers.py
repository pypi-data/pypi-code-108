# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper functions to build model wrappers."""

import abc
import torch
from typing import Any, Dict, Optional

from azureml.automl.dnn.vision.common.base_model_factory import BaseModelFactory
from azureml.automl.dnn.vision.common.base_model_settings import BaseModelSettings
from azureml.automl.dnn.vision.common.constants import ArtifactLiterals, PretrainedModelNames
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException, \
    AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory
from azureml.automl.dnn.vision.object_detection.common.constants import ModelNames, ModelLiterals, \
    RetinaNetLiterals
from azureml.automl.dnn.vision.object_detection.models.base_model_wrapper import \
    BaseObjectDetectionModelWrapper
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.transform import GeneralizedRCNNTransform
from torchvision.transforms import functional, transforms

logger = get_logger(__name__)


def convert_box_score_thresh_to_float_tensor(box_score_thresh_key, **kwargs):
    """If box_score_thresh is present in kwargs, convert it to float32 tensor.

    Inference with onnx model obtained from FasterRCNN model fails in torch 1.7.1 as box_score_thresh
    is interpreted as float64 and float64 is not supported in one of the nodes(Greater).
    Passing it as a torch tensor with float32 type fixes the issue.

    :param box_score_thresh_key: box_score_thresh key
    :type box_score_thresh_key: str
    :param kwargs: Optional keyword arguments
    :type kwargs: dict
    :return: modified keyword arguments
    :rtype: dict
    """
    if box_score_thresh_key in kwargs:
        box_score_thresh = kwargs.get(box_score_thresh_key)
        kwargs[box_score_thresh_key] = torch.tensor(box_score_thresh, dtype=torch.float)
    return kwargs


class CallableGeneralizedRCNNTransform:
    """Wrapper that exposes transforms extracted from GeneralizedRCNNTransform
    to be used when loading data on cpu."""

    def __init__(self, model: torch.nn.Module) -> None:
        """Init method.

        :param model: a model that uses GeneralizedRCNNTransform. FasterRCNN or RetinaNet.
        """
        model_transform: GeneralizedRCNNTransform = model.transform
        self._gen_rcnn_transform = GeneralizedRCNNTransform(min_size=model_transform.min_size,
                                                            max_size=model_transform.max_size,
                                                            image_mean=model_transform.image_mean,
                                                            image_std=model_transform.image_std)

    @staticmethod
    def identity_batch(images):
        """A NOP batch method.

        :param images: images to batch
        :return: same images
        """
        return images

    @staticmethod
    def identity_normalize(image):
        """A NOP normalization method.

        :param image: image to normalize
        :return: same image
        """
        return image

    @staticmethod
    def identity_resize(image, target_index):
        """A NOP resize method.

        :param image: image to resize.
        :param target_index: target index to resize.
        :return: tuple with same image and target_index.
        """
        return image, target_index

    def inference_transform(self, image):
        """Apply the transform from the model on a single image at inference time.

        :param image: the image to prepare for inference
        :type image: PIL Image
        :return: transformed image
        :rtype: Tensor
        """
        self._gen_rcnn_transform.training = False
        # No need for batching here, as this function is called for each image
        self._gen_rcnn_transform.batch_images = self.identity_batch
        image_tensor = functional.to_tensor(image)
        new_image, _ = self._gen_rcnn_transform(torch.unsqueeze(image_tensor, 0))  # transform expects a batch

        # remove the batch dimension
        return new_image.tensors[0]

    def train_validation_transform(self, is_train, image, boxes, masks=None):
        """Exposes model specific transformations.

        :param is_train: True if the transformations are for training, False otherwise.
        :param image: image tensor, 3 dimensions
        :param boxes: boxes tensor
        :param mask: tensors of masks (unnecessary)
        :return: a tuple with new image, boxes, height and width, and optionally new masks
        """

        self._gen_rcnn_transform.training = is_train
        # No need for batching here, as this function is called for each image
        self._gen_rcnn_transform.batch_images = self.identity_batch

        targets = {"boxes": boxes}

        if masks is not None:
            targets['masks'] = masks

        new_image, new_targets = self._gen_rcnn_transform(torch.unsqueeze(image, 0),  # transform expects a batch
                                                          [targets])
        # remove the batch dimension
        new_image = new_image.tensors[0]
        # the first element of the list contains the boxes for the image,
        # as the batch only has one entry

        new_boxes = new_targets[0]["boxes"]
        new_masks = new_targets[0].get("masks", None)

        new_height = new_image.shape[1]
        new_width = new_image.shape[2]

        return new_image, new_boxes, new_height, new_width, new_masks


class FasterRCNNModelSettings(BaseModelSettings):
    """Model settings for Faster RCNN model."""

    def __init__(self, settings: Dict[str, Any]) -> None:
        """Initialize model settings from run settings dictionary.

        :param settings: Settings passed into runner.
        :type settings: dict
        """
        valid_keys = [ModelLiterals.MIN_SIZE, ModelLiterals.MAX_SIZE, ModelLiterals.BOX_SCORE_THRESH,
                      ModelLiterals.BOX_NMS_THRESH, ModelLiterals.BOX_DETECTIONS_PER_IMG]
        self._model_settings = {key: settings[key] for key in valid_keys if key in settings}

    def model_init_kwargs(self):
        """Get kwargs to be used for model initialization.

        :return: kwargs used for initialization
        :rtype: dict
        """
        return self._model_settings

    def get_settings_dict(self):
        """Get settings dict from which model settings object can be re-initialized.

        :return: Settings dictionary
        :rtype: dict
        """
        return self._model_settings


class FasterRCNNResnetFPNWrapper(BaseObjectDetectionModelWrapper, abc.ABC):
    """Model wrapper for Faster RCNN with Resnet FPN backbone."""

    def __init__(self, model_name, number_of_classes, model_state=None, specs=None,
                 model_settings=None, inference_settings=None):
        """
        :param model_name: Name of the resnet model to use as a backbone
        :type string: str
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
        super().__init__(model_name=model_name, number_of_classes=number_of_classes, specs=specs,
                         model_settings=model_settings, inference_settings=inference_settings)

        load_pretrained_model_dict = model_state is None

        self._model = self._create_model(number_of_classes=number_of_classes, specs=specs,
                                         load_pretrained_model_dict=load_pretrained_model_dict)

        if not load_pretrained_model_dict:
            self.load_state_dict(model_state)

    def _create_model(self, number_of_classes, specs=None, load_pretrained_model_dict=True, **kwargs):
        kwargs = {} if self.model_settings is None else self.model_settings.model_init_kwargs()
        kwargs = convert_box_score_thresh_to_float_tensor(ModelLiterals.BOX_SCORE_THRESH, **kwargs)

        model = self._model_constructor(pretrained=True,
                                        load_pretrained_model_dict=load_pretrained_model_dict,
                                        **kwargs)

        if number_of_classes is not None:
            input_features = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(input_features,
                                                              number_of_classes)

        return model

    @property
    def model(self):
        """Returns the wrapped model."""
        return self._model

    @model.setter
    def model(self, value):
        """Sets the wrapped model.

        :param value: the model
        :type value: nn.Module
        """
        self._model = value

    @abc.abstractmethod
    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):
        raise NotImplementedError

    def get_inference_transform(self):
        """Get the transformation function to use at inference time."""
        return CallableGeneralizedRCNNTransform(self.model).inference_transform

    def get_train_validation_transform(self):
        """Get the transformation function to use at training and validation time."""
        model = self.model.module if self._distributed else self.model
        return CallableGeneralizedRCNNTransform(model).train_validation_transform

    def disable_model_transform(self):
        """Disable resize and normalize from the model."""
        model = self.model.module if self._distributed else self.model
        model.transform.resize = CallableGeneralizedRCNNTransform.identity_resize
        model.transform.normalize = CallableGeneralizedRCNNTransform.identity_normalize


class RetinaNetModelSettings(BaseModelSettings):
    """Model settings for Retinat model."""

    def __init__(self, settings: Dict[str, Any]) -> None:
        """Initialize model settings from run settings dictionary.

        :param settings: Settings passed into runner.
        :type settings: dict
        """
        valid_keys = [ModelLiterals.MIN_SIZE, ModelLiterals.MAX_SIZE, ModelLiterals.BOX_SCORE_THRESH,
                      ModelLiterals.BOX_NMS_THRESH, ModelLiterals.BOX_DETECTIONS_PER_IMG]
        self._model_settings = {key: settings[key] for key in valid_keys if key in settings}

    def model_init_kwargs(self):
        """Get kwargs to be used for model initialization.

        :return: kwargs used for initialization
        :rtype: dict
        """
        # Map ModelLiterals to exact keys expected in RetinaNet kwargs
        retinanet_key_mapping = {
            ModelLiterals.MIN_SIZE: RetinaNetLiterals.MIN_SIZE,
            ModelLiterals.MAX_SIZE: RetinaNetLiterals.MAX_SIZE,
            ModelLiterals.BOX_SCORE_THRESH: RetinaNetLiterals.SCORE_THRESH,
            ModelLiterals.BOX_NMS_THRESH: RetinaNetLiterals.NMS_THRESH,
            ModelLiterals.BOX_DETECTIONS_PER_IMG: RetinaNetLiterals.DETECTIONS_PER_IMG
        }
        kwargs = {retinanet_key_mapping[key]: value for key, value in self._model_settings.items()
                  if key in retinanet_key_mapping}
        return kwargs

    def get_settings_dict(self):
        """Get settings dict from which model settings object can be re-initialized.

        :return: Settings dictionary
        :rtype: dict
        """
        return self._model_settings


class FasterRCNNResnet152FPNWrapper(FasterRCNNResnetFPNWrapper):
    """Model wrapper for Faster RCNN with Resnet 152 FPN backbone."""

    def __init__(self, number_of_classes, model_state=None, specs=None,
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
        super().__init__(model_name=ModelNames.FASTER_RCNN_RESNET152_FPN,
                         number_of_classes=number_of_classes, model_state=model_state, specs=specs,
                         model_settings=model_settings, inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.fasterrcnn_resnet152_fpn(pretrained=pretrained,
                                                               load_pretrained_model_dict=load_pretrained_model_dict,
                                                               **kwargs)


class FasterRCNNResnet101FPNWrapper(FasterRCNNResnetFPNWrapper):
    """Model wrapper for Faster RCNN with Resnet 101 FPN backbone."""

    def __init__(self, number_of_classes, model_state=None, specs=None,
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
        super().__init__(model_name=ModelNames.FASTER_RCNN_RESNET101_FPN,
                         number_of_classes=number_of_classes, model_state=model_state, specs=specs,
                         model_settings=model_settings, inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.fasterrcnn_resnet101_fpn(pretrained=pretrained,
                                                               load_pretrained_model_dict=load_pretrained_model_dict,
                                                               **kwargs)


class FasterRCNNResnet50FPNWrapper(FasterRCNNResnetFPNWrapper):
    """Model wrapper for Faster RCNN with Resnet 50 FPN backbone."""

    def __init__(self, number_of_classes, model_state=None, specs=None,
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
        super().__init__(model_name=ModelNames.FASTER_RCNN_RESNET50_FPN,
                         number_of_classes=number_of_classes, model_state=model_state, specs=specs,
                         model_settings=model_settings, inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.fasterrcnn_resnet50_fpn(pretrained=pretrained,
                                                              load_pretrained_model_dict=load_pretrained_model_dict,
                                                              **kwargs)


class FasterRCNNResnet34FPNWrapper(FasterRCNNResnetFPNWrapper):
    """Model wrapper for Faster RCNN with Resnet 34 FPN backbone."""

    def __init__(self, number_of_classes, model_state=None, specs=None,
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
        super().__init__(model_name=ModelNames.FASTER_RCNN_RESNET34_FPN,
                         number_of_classes=number_of_classes, model_state=model_state, specs=specs,
                         model_settings=model_settings, inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.fasterrcnn_resnet34_fpn(pretrained=pretrained,
                                                              load_pretrained_model_dict=load_pretrained_model_dict,
                                                              **kwargs)


class FasterRCNNResnet18FPNWrapper(FasterRCNNResnetFPNWrapper):
    """Model wrapper for Faster RCNN with Resnet 18 FPN backbone."""

    def __init__(self, number_of_classes, model_state=None, specs=None,
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
        super().__init__(model_name=ModelNames.FASTER_RCNN_RESNET18_FPN,
                         number_of_classes=number_of_classes, model_state=model_state, specs=specs,
                         model_settings=model_settings, inference_settings=inference_settings)

    def _model_constructor(self, pretrained, load_pretrained_model_dict, **kwargs):

        return PretrainedModelFactory.fasterrcnn_resnet18_fpn(pretrained=pretrained,
                                                              load_pretrained_model_dict=load_pretrained_model_dict,
                                                              **kwargs)


class RetinaNetResnet50FPNWrapper(BaseObjectDetectionModelWrapper):
    """Model wrapper for RetinaNet with Resnet50 FPN backbone."""

    def __init__(self, number_of_classes, model_state=None, specs=None,
                 model_name=ModelNames.RETINANET_RESNET50_FPN, model_settings=None, inference_settings=None):
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

        super().__init__(model_name=model_name, number_of_classes=number_of_classes, specs=specs,
                         model_settings=model_settings, inference_settings=inference_settings)

        load_pretrained_model_dict = model_state is None

        self._model = self._create_model(number_of_classes=number_of_classes, specs=specs,
                                         load_pretrained_model_dict=load_pretrained_model_dict)

        if not load_pretrained_model_dict:
            self.load_state_dict(model_state)

    @property
    def model(self):
        """Returns the wrapped model."""
        return self._model

    @model.setter
    def model(self, value):
        """Sets the wrapped model.

        :param value: the model
        :type value: nn.Module
        """
        self._model = value

    def _create_model(self, number_of_classes, specs=None, load_pretrained_model_dict=True):
        kwargs = {} if self.model_settings is None else self.model_settings.model_init_kwargs()
        kwargs = convert_box_score_thresh_to_float_tensor(RetinaNetLiterals.SCORE_THRESH, **kwargs)
        model = PretrainedModelFactory.retinanet_restnet50_fpn(pretrained=True,
                                                               load_pretrained_model_dict=load_pretrained_model_dict,
                                                               num_classes=number_of_classes,
                                                               **kwargs)
        return model

    def get_inference_transform(self):
        """Get the transformation function to use at inference time."""
        return CallableGeneralizedRCNNTransform(self.model).inference_transform

    def get_train_validation_transform(self):
        """Get the transformation function to use at training and validation time."""
        model = self.model.module if self._distributed else self.model
        return CallableGeneralizedRCNNTransform(model).train_validation_transform

    def disable_model_transform(self):
        """Disable resize and normalize from the model."""
        model = self.model.module if self._distributed else self.model
        model.transform.resize = CallableGeneralizedRCNNTransform.identity_resize
        model.transform.normalize = CallableGeneralizedRCNNTransform.identity_normalize

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
                                           input_names=['input'], output_names=['boxes', 'scores', 'labels'],
                                           dynamic_axes={'input': {0: 'batch'},
                                                         'boxes': {0: 'prediction'},
                                                         'labels': {0: 'prediction'},
                                                         'scores': {0: 'prediction'}})


class ObjectDetectionModelFactory(BaseModelFactory):
    """Factory function to create models."""

    def __init__(self) -> None:
        """Init method."""
        super().__init__()

        self._models_dict = {
            ModelNames.FASTER_RCNN_RESNET18_FPN: FasterRCNNResnet18FPNWrapper,
            ModelNames.FASTER_RCNN_RESNET34_FPN: FasterRCNNResnet34FPNWrapper,
            ModelNames.FASTER_RCNN_RESNET50_FPN: FasterRCNNResnet50FPNWrapper,
            ModelNames.FASTER_RCNN_RESNET101_FPN: FasterRCNNResnet101FPNWrapper,
            ModelNames.FASTER_RCNN_RESNET152_FPN: FasterRCNNResnet152FPNWrapper,
            ModelNames.RETINANET_RESNET50_FPN: RetinaNetResnet50FPNWrapper
        }

        self._pre_trained_model_names_dict = {
            ModelNames.FASTER_RCNN_RESNET18_FPN: PretrainedModelNames.FASTERRCNN_RESNET18_FPN_COCO,
            ModelNames.FASTER_RCNN_RESNET34_FPN: PretrainedModelNames.FASTERRCNN_RESNET34_FPN_COCO,
            ModelNames.FASTER_RCNN_RESNET50_FPN: PretrainedModelNames.FASTERRCNN_RESNET50_FPN_COCO,
            ModelNames.FASTER_RCNN_RESNET101_FPN: PretrainedModelNames.FASTERRCNN_RESNET101_FPN_COCO,
            ModelNames.FASTER_RCNN_RESNET152_FPN: PretrainedModelNames.FASTERRCNN_RESNET152_FPN_COCO,
            ModelNames.RETINANET_RESNET50_FPN: PretrainedModelNames.RETINANET_RESNET50_FPN_COCO
        }

        self._model_settings_dict = {
            ModelNames.FASTER_RCNN_RESNET18_FPN: FasterRCNNModelSettings,
            ModelNames.FASTER_RCNN_RESNET34_FPN: FasterRCNNModelSettings,
            ModelNames.FASTER_RCNN_RESNET50_FPN: FasterRCNNModelSettings,
            ModelNames.FASTER_RCNN_RESNET101_FPN: FasterRCNNModelSettings,
            ModelNames.FASTER_RCNN_RESNET152_FPN: FasterRCNNModelSettings,
            ModelNames.RETINANET_RESNET50_FPN: RetinaNetModelSettings
        }

        self._default_model = ModelNames.FASTER_RCNN_RESNET50_FPN

    def get_model_wrapper(self, number_of_classes, model_name=None, model_state=None, specs=None,
                          settings={}):
        """ Get the wrapper for a fasterrcnn model

        :param number_of_classes: number of classes in object detection
        :type number_of_classes: int
        :param model_name: string name of the model
        :type model_name: str
        :param model_state: model weights
        :type model_state: dict
        :param specs: model specifications
        :type specs: dict
        :param settings: Settings to initialize model settings from
        :type settings: dict
        """

        if model_name is None:
            model_name = self._default_model

        if model_name not in self._models_dict:
            raise AutoMLVisionValidationException("The provided model_name is not supported.",
                                                  has_pii=False)

        if model_name not in self._model_settings_dict:
            raise AutoMLVisionSystemException("Model name {} does not have corresponding model settings class."
                                              .format(model_name))
        model_settings = self._model_settings_dict[model_name](settings=settings)

        from azureml.automl.dnn.vision.object_detection.common.object_detection_utils import get_inference_settings
        inference_settings = get_inference_settings(settings=settings)

        return self._models_dict[model_name](number_of_classes=number_of_classes,
                                             model_state=model_state,
                                             specs=specs,
                                             model_settings=model_settings,
                                             inference_settings=inference_settings)
