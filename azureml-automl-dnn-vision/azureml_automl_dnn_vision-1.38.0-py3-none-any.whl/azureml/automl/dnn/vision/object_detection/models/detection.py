# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Convenience functions to create model wrappers."""

import torch
from typing import Union
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.constants import TrainingLiterals
from azureml.automl.dnn.vision.object_detection.models.base_model_wrapper import \
    BaseObjectDetectionModelWrapper
from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
from .object_detection_model_wrappers import ObjectDetectionModelFactory
from .instance_segmentation_model_wrappers import InstanceSegmentationModelFactory
from ..common.constants import ModelNames


def setup_model(model_name, number_of_classes, classes, device, distributed=False, rank=None,
                model_state=None, specs=None, settings={}) -> Union[BaseObjectDetectionModelWrapper, YoloV5Wrapper]:
    """Returns model wrapper from name and number of classes.

    :param model_name: Name of model to get
    :type model_name: str
    :param number_of_classes: Number of classes
    :type number_of_classes: int
    :param classes: list of class names
    :type classes: List
    :param device: device to use
    :type device: torch.device
    :param distributed: flag that indicates if the model is going to be used in distributed mode
    :type distributed: bool
    :param rank: rank of the process in distributed mode
    :type rank: int
    :param model_state: model weights
    :type model_state: dict
    :param specs: model specifications
    :type specs: dict
    :param settings: Settings to initialize model settings from.
    :type settings: dict
    :return: Model wrapper containing model
    :rtype: Object derived from BaseObjectDetectionModelWrapper (See object_detection.model.base_model_wrapper)
    """

    # TODO: this is temporary, the next refactoring step is to use the ObjectDetectionModelFactory
    if model_name == ModelNames.YOLO_V5:
        specs.update(settings)
        model_wrapper: Union[BaseObjectDetectionModelWrapper, YoloV5Wrapper] = _setup_yolo_model(
            model_name, number_of_classes, model_state, specs)
        # Extract layer_to_freeze from specs for yolov5
        layers_to_freeze = specs.get(TrainingLiterals.LAYERS_TO_FREEZE, None)
    else:
        object_detection_model_factory = ObjectDetectionModelFactory()
        instance_segmentation_model_factory = InstanceSegmentationModelFactory()

        model_factory: Union[ObjectDetectionModelFactory, InstanceSegmentationModelFactory]
        if instance_segmentation_model_factory.model_supported(model_name):
            model_factory = instance_segmentation_model_factory  # Type: InstanceSegmentationModelFactory
        else:
            model_factory = object_detection_model_factory  # Type: ObjectDetectionModelFactory

        model_wrapper = model_factory.get_model_wrapper(
            model_name=model_name, number_of_classes=number_of_classes,
            model_state=model_state, specs=specs, settings=settings)
        # Extract layer_to_freeze from settings for all the others
        layers_to_freeze = settings.get(TrainingLiterals.LAYERS_TO_FREEZE, None)

    # Freeze layers
    # make sure to have this logic before setting up ddp
    if layers_to_freeze is not None:
        utils.freeze_model_layers(model_wrapper, layers_to_freeze=layers_to_freeze)

    model_wrapper.classes = classes
    model_wrapper.device = device

    # Move base model to device
    model_wrapper.to_device(device)

    if distributed:
        # TODO: https://github.com/python/mypy/issues/9160
        model_wrapper.model = torch.nn.parallel.DistributedDataParallel(model_wrapper.model,  # type: ignore[misc]
                                                                        device_ids=[rank],
                                                                        output_device=rank)
    model_wrapper.distributed = distributed

    return model_wrapper


def _setup_yolo_model(model_name, number_of_classes, model_state, specs):
    from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
    model_wrapper = YoloV5Wrapper(model_name, number_of_classes, specs, model_state)

    # TODO: temporary hack to reduce the amount of refactoring; replace with proper
    # attributes on the model wrapper
    model_wrapper.model.hyp = specs
    model_wrapper.model.nc = number_of_classes

    return model_wrapper


def use_bg_label(model_name):
    """ Returns if the background(--bg--) label should be used with the model.

    :param model_name: Model name
    :type model_name: str
    :return: Whether to use bg label or not
    :rtype: bool
    """
    if model_name == ModelNames.YOLO_V5 or model_name == ModelNames.RETINANET_RESNET50_FPN:
        return False
    return True
