# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Concrete classes for model wrappers."""
import abc
import torch
from timm.models.vision_transformer import checkpoint_filter_fn
from torch import nn
from typing import Optional

from azureml.automl.dnn.vision.classification.common.constants import ModelNames, \
    ModelLiterals, ModelParameters
from azureml.automl.dnn.vision.classification.models.base_model_wrapper import BaseModelWrapper
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.base_model_factory import BaseModelFactory
from azureml.automl.dnn.vision.common.constants import PretrainedModelNames, TrainingLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory

logger = get_logger(__name__)


class Resnet18Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet18."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.resnet18(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET18,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class Resnet34Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet34."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.resnet34(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET34,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class Resnet50Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet50."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.resnet50(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET50,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class Resnet101Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet101."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.resnet101(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET101,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class Resnet152Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet152."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.resnet152(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET152,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class Mobilenetv2Wrapper(BaseModelWrapper):
    """Model wrapper for mobilenetv2."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.mobilenet_v2(pretrained=pretrained)
        num_feats = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.MOBILENETV2,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class SeresnextWrapper(BaseModelWrapper):
    """Model wrapper for seresnext."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.se_resnext50_32x4d(num_classes=1000, pretrained=pretrained,
                                                          pretrained_on='imagenet')
        num_feats = model.last_linear.in_features
        model.last_linear = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])

        # seresnext50 can't take arbitrary image size
        default_valid_resize_size = ModelParameters.DEFAULT_VALID_RESIZE_SIZE
        default_valid_crop_size = ModelParameters.DEFAULT_VALID_CROP_SIZE
        default_train_crop_size = ModelParameters.DEFAULT_TRAIN_CROP_SIZE
        if valid_resize_size != default_valid_resize_size or valid_crop_size != default_valid_crop_size or \
                train_crop_size != default_train_crop_size:
            logger.warning("[{} only takes a fixed input size ({}: {}, {}: {} and {}: {}) "
                           "thus using defaults instead of the provided values]"
                           .format(ModelNames.SERESNEXT,
                                   ModelLiterals.VALID_RESIZE_SIZE, default_valid_resize_size,
                                   ModelLiterals.VALID_CROP_SIZE, default_valid_crop_size,
                                   ModelLiterals.TRAIN_CROP_SIZE, default_train_crop_size))
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=default_valid_resize_size, valid_crop_size=default_valid_crop_size,
                         train_crop_size=default_train_crop_size, multilabel=multilabel,
                         model_name=ModelNames.SERESNEXT, featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class ResNest50Wrapper(BaseModelWrapper):
    """ Model wrapper for ResNest-50."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.resnest50(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNEST50,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class ResNest101Wrapper(BaseModelWrapper):
    """ Model wrapper for ResNest-101."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        model = PretrainedModelFactory.resnest101(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNEST101,
                         featurizer=featurizer)

        if model_state is not None:
            self.load_state_dict(model_state)


class ViTBaseModelWrapper(BaseModelWrapper, abc.ABC):
    """ Base Model wrapper for vit models"""

    def __init__(self, model_name: str, num_classes: int, valid_resize_size: int, valid_crop_size: int,
                 train_crop_size: int, multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param model_name: Model name
        :type model_name: str
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        pretrained = model_state is None

        if train_crop_size != valid_crop_size:
            train_crop_size = valid_crop_size
            logger.warning("[{} doesn't support different values for {} and {}. Using {} for both. "
                           "({}:{} and {}:{})]".format(model_name, ModelLiterals.TRAIN_CROP_SIZE,
                                                       ModelLiterals.VALID_CROP_SIZE, ModelLiterals.VALID_CROP_SIZE,
                                                       ModelLiterals.TRAIN_CROP_SIZE, train_crop_size,
                                                       ModelLiterals.VALID_CROP_SIZE, valid_crop_size))

        model = self._model_constructor(pretrained=pretrained, img_size=valid_crop_size)

        num_feats = model.head.in_features
        model.head = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        featurizer.forward = model.forward_features

        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=model_name,
                         featurizer=featurizer)

        if model_state is not None:
            # To resize pos embedding when when training crop size and scoring/featurization crop size are different
            model_state = checkpoint_filter_fn(model_state, model)
            self.load_state_dict(model_state)

    @abc.abstractmethod
    def _model_constructor(self, pretrained, img_size):
        raise NotImplementedError


class ViTB16R224Wrapper(ViTBaseModelWrapper):
    """ Model wrapper for the default vit model: ViT-base-patch16-r224."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        # feature_dim = 768
        super().__init__(model_name=ModelNames.VITB16R224, num_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_state=model_state)

    def _model_constructor(self, pretrained, img_size):
        return PretrainedModelFactory.vitb16r224(pretrained=pretrained, img_size=img_size)


class ViTS16R224Wrapper(ViTBaseModelWrapper):
    """ Model wrapper for the faster vit model: ViT-small-patch16-r224."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        # feature_dim=384
        super().__init__(model_name=ModelNames.VITS16R224, num_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_state=model_state)

    def _model_constructor(self, pretrained, img_size):
        return PretrainedModelFactory.vits16r224(pretrained=pretrained, img_size=img_size)


class ViTL16R224Wrapper(ViTBaseModelWrapper):
    """ Model wrapper for the larger vit model: ViT-large-patch16-r224."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, model_state: Optional[dict] = None) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param model_state: model weights
        :type model_state: Optional[dict]
        """
        # feature_dim=1024
        super().__init__(model_name=ModelNames.VITL16R224, num_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_state=model_state)

    def _model_constructor(self, pretrained, img_size):
        return PretrainedModelFactory.vitl16r224(pretrained=pretrained, img_size=img_size)


class ModelFactory(BaseModelFactory):
    """Model factory class for obtaining model wrappers."""

    def __init__(self):
        """Init method."""
        super().__init__()

        self._models_dict = {
            ModelNames.RESNET18: Resnet18Wrapper,
            ModelNames.RESNET34: Resnet34Wrapper,
            ModelNames.RESNET50: Resnet50Wrapper,
            ModelNames.RESNET101: Resnet101Wrapper,
            ModelNames.RESNET152: Resnet152Wrapper,
            ModelNames.MOBILENETV2: Mobilenetv2Wrapper,
            ModelNames.SERESNEXT: SeresnextWrapper,
            ModelNames.RESNEST50: ResNest50Wrapper,
            ModelNames.RESNEST101: ResNest101Wrapper,
            ModelNames.VITB16R224: ViTB16R224Wrapper,
            ModelNames.VITS16R224: ViTS16R224Wrapper,
            ModelNames.VITL16R224: ViTL16R224Wrapper,
        }

        self._pre_trained_model_names_dict = {
            ModelNames.RESNET18: PretrainedModelNames.RESNET18,
            ModelNames.RESNET34: PretrainedModelNames.RESNET34,
            ModelNames.RESNET50: PretrainedModelNames.RESNET50,
            ModelNames.RESNET101: PretrainedModelNames.RESNET101,
            ModelNames.RESNET152: PretrainedModelNames.RESNET152,
            ModelNames.MOBILENETV2: PretrainedModelNames.MOBILENET_V2,
            ModelNames.SERESNEXT: PretrainedModelNames.SE_RESNEXT50_32X4D,
            ModelNames.RESNEST50: PretrainedModelNames.RESNEST50,
            ModelNames.RESNEST101: PretrainedModelNames.RESNEST101,
            ModelNames.VITB16R224: PretrainedModelNames.VITB16R224,
            ModelNames.VITS16R224: PretrainedModelNames.VITS16R224,
            ModelNames.VITL16R224: PretrainedModelNames.VITL16R224,
        }

        self._default_model = ModelNames.SERESNEXT

    def get_model_wrapper(self, model_name: str, num_classes: int, multilabel: bool,
                          device: torch.device, distributed: bool, rank: int, settings: dict = {},
                          model_state: Optional[dict] = None):
        """
        :param model_name: string name of the model
        :type model_name: str
        :param num_classes: number of classes
        :type num_classes: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param device: device to place the model on
        :type device: torch.device
        :param distributed: if we are in distributed mode
        :type distributed: bool
        :param rank: rank of the process in distributed mode
        :type rank: int
        :param settings: Settings to initialize model settings from
        :type settings: dict
        :param model_state: model weights
        :type model_state: Optional[dict]
        :return: model wrapper
        :rtype: azureml.automl.dnn.vision.classification.base_model_wrappers.BaseModelWrapper
        """
        if model_name is None:
            model_name = self._default_model

        if model_name not in self._models_dict:
            raise AutoMLVisionValidationException('The provided model_name is not supported.',
                                                  has_pii=False)
        if num_classes is None:
            raise AutoMLVisionValidationException('num_classes cannot be None', has_pii=False)

        # Extract relevant parameters from settings
        valid_resize_size = settings.get(ModelLiterals.VALID_RESIZE_SIZE, ModelParameters.DEFAULT_VALID_RESIZE_SIZE)
        valid_crop_size = settings.get(ModelLiterals.VALID_CROP_SIZE, ModelParameters.DEFAULT_VALID_CROP_SIZE)
        train_crop_size = settings.get(ModelLiterals.TRAIN_CROP_SIZE, ModelParameters.DEFAULT_TRAIN_CROP_SIZE)
        model_wrapper = self._models_dict[model_name](num_classes=num_classes,
                                                      valid_resize_size=valid_resize_size,
                                                      valid_crop_size=valid_crop_size,
                                                      train_crop_size=train_crop_size,
                                                      multilabel=multilabel,
                                                      model_state=model_state)

        # Freeze layers
        # make sure to have this logic before setting up ddp
        layers_to_freeze = settings.get(TrainingLiterals.LAYERS_TO_FREEZE, None)
        if layers_to_freeze is not None:
            utils.freeze_model_layers(model_wrapper, layers_to_freeze=layers_to_freeze)

        model_wrapper.to_device(device)

        if distributed:
            model_wrapper.model = nn.parallel.DistributedDataParallel(model_wrapper.model,
                                                                      device_ids=[rank],
                                                                      output_device=rank)
        model_wrapper.distributed = distributed

        return model_wrapper
