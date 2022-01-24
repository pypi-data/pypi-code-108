# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper classes that define object detection model behavior."""

from abc import ABC, abstractmethod
import torch
import time
from PIL.Image import Image

from torchvision.transforms import functional
from torchvision import transforms
from torchvision.ops._register_onnx_ops import _onnx_opset_version

from ..common.boundingbox import BoundingBox
from ..common.constants import OutputFields
from ...common.constants import ArtifactLiterals
from ...common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.base_model_settings import BaseModelSettings
from typing import Any, Dict, List, Optional


logger = get_logger(__name__)


class PredictBoundingBoxMixin:
    """Helper mixin to BaseObjectDetectionModelWrapper that adds prediction methods"""

    def predict(self, images: List[Image]):  # TODO: pass device, model, classes as arguments here
        """Predicts bounding boxes from images.

        :param images: Batch of images
        :type images: List[Image]
        :return: Lists of BoundingBox objects scores
        :rtype: List[azureml.automl.dnn.vision.object_detection.common.boundingbox.BoundingBox]
        """
        inputs = self._get_tensor(images)

        # move tensors to the same device as model
        inputs = inputs.to(self.device)  # type: ignore[attr-defined] # TODO: Define the variable in the subclass
        # change training state of model
        orig_state_train = False
        model = self.model  # type: ignore[attr-defined] # TODO: Define the variable in the subclass
        if model.training:
            model.eval()
            orig_state_train = True

        outputs = model(inputs)

        if orig_state_train:
            model.train()

        # TODO: Ignoring below. Define the variable in the subclass
        return self._get_lists_of_bounding_boxes(self.classes, outputs)  # type: ignore[attr-defined]

    def _get_lists_of_bounding_boxes(self, classes, model_outputs=None):
        """
        :param model_outputs: model output from running the object detection model
        :type model_outputs: List of Dict of lists of boxes, classes and scores
        :return:
        """
        results = []
        for per_image_result in model_outputs:
            boxes = per_image_result[OutputFields.BOXES_LABEL]
            labels = per_image_result[OutputFields.CLASSES_LABEL]
            scores = per_image_result[OutputFields.SCORES_LABEL]

            labels = [classes[index] for index in labels]

            results.append(self._get_list_of_bounding_boxes_for_image(boxes, labels, scores))

        return results

    def _get_list_of_bounding_boxes_for_image(self, boxes=None, labels=None, scores=None):
        """
        :param boxes: FloatTensor sized n x 4 where each box is [top_left_x1, top_left_y1, bottom_right_x2,
        bottom_right_y2]
        :type boxes: torch.FloatTensor
        :param labels: Int64Tensor of size n containing predicted labels for each box
        :type labels: torch.Int64Tensor
        :param scores: float tensor of size n containing scores for each prediction
        :type scores: torch.FloatTensor
        :return: list of BoundingBoxes
        :rtype: List[BoundingBox]
        """
        boxes = []
        for box, label, score in zip(boxes, labels, scores):
            boxes.append(BoundingBox(label, box, score))

        return boxes

    @staticmethod
    def _get_tensor(images=None):
        """
        :param images: list of PIL Image objects
        :type images: List[Image]
        :return: tensor for image batch
        :rtype: torch.Tensor
        """
        return torch.stack([transforms.ToTensor()(im) for im in images], dim=0)


class BaseObjectDetectionModelWrapper(ABC, PredictBoundingBoxMixin):
    """Abstract base class that defines behavior of object detection models."""

    def __init__(self, model_name: str, number_of_classes: int, specs: Optional[Dict[str, Any]] = None,
                 model_settings: Optional[BaseModelSettings] = None,
                 inference_settings: Optional[Dict[str, Any]] = None) -> None:
        """
        :param model_name: Model name
        :type model_name: str
        :param number_of_classes: Number of object classes
        :type number_of_classes: int
        :param specs: specifications for creating the model
        :type specs: dict
        :param model_settings: Optional argument to define model settings
        :type model_settings: BaseModelSettings
        :param inference_settings: Optional argument to define inference settings to use with this model
        :type inference_settings: Optional[Dict[str, Any]]
        """
        self._model_name = model_name
        self._specs = specs
        self._number_of_classes = number_of_classes
        self._model_settings = model_settings
        self._inference_settings = inference_settings
        self._classes = None
        self._device: Optional[str] = None
        self._distributed = False

    @abstractmethod
    def _create_model(self, number_of_classes, specs, **kwargs):
        """Abstract method defining how to create a model from
        number of classes required and model specific specifications.

        :param number_of_classes: Number of classes
        :type number_of_classes: int
        :param specs: Model specifications
        :type specs: Class containing specifications
        :param kwargs: Keyword arguments
        :type kwargs: dict
        """
        pass

    # https://github.com/python/mypy/issues/4165
    @property  # type: ignore[misc]
    @abstractmethod
    def model(self):
        """Returns the model that is being wrapped by this instance."""
        pass

    # https://github.com/python/mypy/issues/4165
    @model.setter  # type: ignore[misc]
    @abstractmethod
    def model(self, value):
        """Sets the model that is being wrapped by this instance."""
        pass

    def _export_onnx_model_with_names(self, file_path: str, device: Optional[str], enable_norm: bool,
                                      input_names, output_names, dynamic_axes):
        """
        Export the pytorch model to onnx model file with specific input_names, output_names and dynamic_axes.

        :param file_path: file path to save the exported onnx model.
        :type file_path: str
        :param device: device where model should be run (usually 'cpu' or 'cuda:0' if it is the first gpu)
        :type device: str
        :param enable_norm: enable normalization when exporting onnx
        :type enable_norm: bool
        :param input_names: Input names parameter to be passed to torch.onnx.export (See torch.onnx.export)
        :type input_names: list
        :param output_names: Output names parameter to be passed to torch.onnx.export (See torch.onnx.export)
        :type output_names: list
        :param dynamic_axes: dynamic_axes parameter to be passed to torch.onnx.export (See torch.onnx.export)
        :type dynamic_axes: dict
        """
        # TODO: support batch inferencing w/ different image size
        # p0 (torchvision==0.7.0): device='cuda:0' is NOT working -- Device mismatch error from detection/rpn.py
        onnx_export_start = time.time()

        class ModelNormalizerWrapper(torch.nn.Module):
            def __init__(self, model: torch.nn.Module) -> None:
                super(ModelNormalizerWrapper, self).__init__()
                self.model = model

            def forward(self, x):
                norm_x = self.normalize(x)
                output = self.model(norm_x)
                return output

            def normalize(self, imgs):
                new_imgs = imgs.clone()
                new_imgs /= 255
                return new_imgs

        dummy_input = torch.randn(1, 3, 600, 800).to(device='cpu')
        if self._distributed:
            new_model = self.model.module
        else:
            new_model = self.model

        new_model.to(device='cpu')
        new_model.eval()
        if enable_norm:
            dummy_input *= 255.
            new_model = ModelNormalizerWrapper(new_model)
        torch.onnx.export(new_model,
                          dummy_input,
                          file_path,
                          opset_version=_onnx_opset_version,
                          input_names=input_names, output_names=output_names,
                          dynamic_axes=dynamic_axes)
        onnx_export_time = time.time() - onnx_export_start
        logger.info('ONNX ({}) export time {:.4f} with enable_onnx_normalization ({})'
                    .format(file_path, onnx_export_time, enable_norm))

    def export_onnx_model(self, file_path=ArtifactLiterals.ONNX_MODEL_FILE_NAME, device=None, enable_norm=False):
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
                                           input_names=['input'], output_names=['boxes', 'labels', 'scores'],
                                           dynamic_axes={'input': {0: 'batch'},
                                                         'boxes': {0: 'prediction'},
                                                         'labels': {0: 'prediction'},
                                                         'scores': {0: 'prediction'}})

    def state_dict(self):
        """Get the state dictionary from pytorch model

        :return: State dictionary
        :rtype: dict
        """
        if self._distributed:
            return self.model.module.state_dict()
        return self.model.state_dict()

    def load_state_dict(self, state_dict, strict=True):
        """Set the state dictionary for pytorch model

        :param state_dict: State dictionary
        :type state_dict: dict
        :param strict: if strict mapping is required
        :type strict: bool
        """
        if self._distributed:
            self.model.module.load_state_dict(state_dict, strict)
        else:
            self.model.load_state_dict(state_dict, strict)

    @property
    def device(self):
        """Get device for pytorch model

        :return: device
        :rtype: str
        """
        return self._device

    @device.setter
    def device(self, value):
        """Set device for pytorch model

        :param value: device
        :type value: str
        """
        self._device = value

    @property
    def model_name(self):
        """Get model name

        :return: name of the model that is used
        :rtype: str
        """
        return self._model_name

    @model_name.setter
    def model_name(self, value):
        """Set model name

        :param value: model name
        :type value: str
        """
        self._model_name = value

    @property
    def parameters(self):
        """Get model parameters

        :return: Model parameters
        :rtype: Pytorch state dictionary
        """
        return self.model.parameters

    @property
    def classes(self):
        """Get the classes in a list that corresponds to class index

        :return: List of class names. If none is set, will simply return ['0', '1', '2',....]
        :rtype: List of strings
        """
        if self._classes is not None:
            return self._classes
        else:
            numeric_map = [str(i) for i in range(self._number_of_classes)]
            return numeric_map

    @classes.setter
    def classes(self, classes):
        """Set the image classes

        :param classes: Names of the different classes found in image
        :type classes: List of strings
        """
        self._classes = classes

    @property
    def number_of_classes(self):
        """Get the number of classes

        :return: number of classes for this model
        :rtype: int
        """
        return self._number_of_classes

    @property
    def specs(self):
        """Get the model specifications

        :return: model specifications
        :rtype: dict
        """
        return self._specs

    @property
    def model_settings(self):
        """Get the model settings

        :return: model settings
        :rtype: BaseModelSettings
        """
        return self._model_settings

    @property
    def inference_settings(self):
        """Get the inference settings to use with this model

        :return: inference settings
        :rtype: Dict[str, Any]
        """
        return self._inference_settings

    def to_device(self, device: str):
        """Send to device.

        :param device: device to which the model should be moved to
        :type device: str
        """
        self.model.to(device)
        self._device = device

    @property
    def distributed(self):
        """Get if the model is a DistributedDataParallel model.

        :return: distributed
        :rtype: bool
        """
        return self._distributed

    @distributed.setter
    def distributed(self, value):
        """Set flag to indicate the model is a DistributedDataParallel model.

        :param value: distributed
        :type value: bool
        """
        self._distributed = value

    def get_inference_transform(self):
        """Get the transformation function to use at inference time."""
        return functional.to_tensor

    def get_train_validation_transform(self):
        """Get the transformation function to use at training and validation time."""
        return None

    def disable_model_transform(self):
        """Disable resize and normalize from the model - NOP in general case."""
        pass
