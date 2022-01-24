# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Pretrained model utilities for the package."""
from typing import Optional, Dict, Any, List
from urllib.error import URLError, ContentTooShortError

import torch.nn
from pretrainedmodels.models.senet import SENet, SEResNeXtBottleneck, pretrained_settings
from resnest.torch import resnest50, resnest101

import torch
from timm import create_model
from timm.models.vision_transformer import VisionTransformer
from timm.models.helpers import load_pretrained
from timm.models.vision_transformer import checkpoint_filter_fn

from torchvision.models.detection.backbone_utils import BackboneWithFPN
from torchvision.models.detection.faster_rcnn import FasterRCNN
from torchvision.models.detection.mask_rcnn import MaskRCNN
from torchvision.models.detection.retinanet import RetinaNet
from torchvision.models.mobilenet import MobileNetV2
from torchvision.models.resnet import ResNet, BasicBlock, Bottleneck
from torchvision.models.utils import load_state_dict_from_url
from torchvision.ops import misc as misc_nn_ops
from torchvision.ops.feature_pyramid_network import LastLevelMaxPool, LastLevelP6P7

from .constants import PretrainedModelNames, PretrainedModelUrls, PretrainedSettings
from .exceptions import AutoMLVisionSystemException
from .logging_utils import get_logger
from .torch_utils import intersect_dicts

logger = get_logger(__name__)


class PretrainedModelFactory:
    """The Factory class of creating the pretrained models that are used by the package."""

    @staticmethod
    def _load_state_dict_from_url_with_retry(url: str, progress: bool = True,
                                             check_hash: bool = True, **kwargs: Any) -> Any:
        """Fetch state dict from a url.

        :param url: Url to download state dict from
        :type url: str
        :param progress: Whether or not to display download progress
                         (see torchvision.models.utils.load_state_dict_from_url)
        :type progress: bool
        :param check_hash: Whether or not to check hash of the downloaded file
                           (see torchvision.models.utils.load_state_dict_from_url)
        :type check_hash: bool
        :param kwargs: keywords args for torchvision.models.utils.load_state_dict_from_url
        :type kwargs: dict
        :return: state dict for torch model
        :rtype: dict
        """

        for i in range(PretrainedSettings.DOWNLOAD_RETRY_COUNT - 1):
            try:
                return load_state_dict_from_url(url, progress=progress, check_hash=check_hash, **kwargs)
            except (ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
                    URLError, ContentTooShortError, RuntimeError) as e:
                logger.warning('Encountered {} error while loading state dict. Retry count: {}. Error details: {}'
                               .format(e.__class__.__name__, i + 1, e))

        logger.warning("Failed loading state dict, will try to load for one last time."
                       "If failed again, please retry by submitting a new run.")
        return load_state_dict_from_url(url, progress=progress, check_hash=check_hash, **kwargs)

    @staticmethod
    def download_pretrained_model_weights(model_name: str, progress: bool = True) -> None:
        """Fetch pretrained state dict from a url and download to a local path.

        :param model_name: Name of the pretrained model.
        :type model_name: PretrainedModelNames
        :param progress: If True, displays a progress bar of the download to stderr
        :type progress: bool
        """
        PretrainedModelFactory._load_state_dict_from_url_with_retry(
            PretrainedModelUrls.MODEL_URLS[model_name], progress=progress)

    @staticmethod
    def resnest50(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> Any:
        r"""ResNest-50 model from
        `"ResNeSt: Split-Attention Networks" <https://arxiv.org/pdf/2004.08955.pdf>`_

        :param pretrained: If True, returns a model pre-trained on ImageNet
        :type pretrained: bool
        :param progress: If True, displays a progress bar of the download to stderr
        :type progress: bool
        :param kwargs: kwargs to pass to model
        :type kwargs: dict
        """
        model = resnest50(pretrained=False, **kwargs)
        if pretrained:
            state_dict = PretrainedModelFactory._load_state_dict_from_url_with_retry(
                PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.RESNEST50], progress=progress)
            model.load_state_dict(state_dict)
        return model

    @staticmethod
    def resnest101(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> Any:
        r"""ResNest-101 model from
        `"ResNeSt: Split-Attention Networks" <https://arxiv.org/pdf/2004.08955.pdf>`_

        :param pretrained: If True, returns a model pre-trained on ImageNet
        :type pretrained: bool
        :param progress: If True, displays a progress bar of the download to stderr
        :type progress: bool
        :param kwargs: kwargs to pass to model
        :type kwargs: dict
        """
        model = resnest101(pretrained=False, **kwargs)
        if pretrained:
            state_dict = PretrainedModelFactory._load_state_dict_from_url_with_retry(
                PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.RESNEST101], progress=progress)
            model.load_state_dict(state_dict)
        return model

    @staticmethod
    def resnet18(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
        r"""ResNet-18 model from
        `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
            progress (bool): If True, displays a progress bar of the download to stderr
        """
        return PretrainedModelFactory._resnet(PretrainedModelNames.RESNET18,
                                              BasicBlock,
                                              [2, 2, 2, 2],
                                              pretrained,
                                              progress,
                                              **kwargs)

    @staticmethod
    def resnet34(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
        r"""ResNet-34 model from
        `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
            progress (bool): If True, displays a progress bar of the download to stderr
        """
        return PretrainedModelFactory._resnet(PretrainedModelNames.RESNET34,
                                              BasicBlock,
                                              [3, 4, 6, 3],
                                              pretrained,
                                              progress,
                                              **kwargs)

    @staticmethod
    def resnet50(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
        r"""ResNet-50 model from
        `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
            progress (bool): If True, displays a progress bar of the download to stderr
        """
        return PretrainedModelFactory._resnet(PretrainedModelNames.RESNET50,
                                              Bottleneck,
                                              [3, 4, 6, 3],
                                              pretrained,
                                              progress,
                                              **kwargs)

    @staticmethod
    def resnet101(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
        r"""ResNet-101 model from
        `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
            progress (bool): If True, displays a progress bar of the download to stderr
        """
        return PretrainedModelFactory._resnet(PretrainedModelNames.RESNET101,
                                              Bottleneck,
                                              [3, 4, 23, 3],
                                              pretrained,
                                              progress,
                                              **kwargs)

    @staticmethod
    def resnet152(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
        r"""ResNet-152 model from
        `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
            progress (bool): If True, displays a progress bar of the download to stderr
        """
        return PretrainedModelFactory._resnet(PretrainedModelNames.RESNET152,
                                              Bottleneck,
                                              [3, 8, 36, 3],
                                              pretrained,
                                              progress,
                                              **kwargs)

    @staticmethod
    def mobilenet_v2(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> MobileNetV2:
        """
        Constructs a MobileNetV2 architecture from
        `"MobileNetV2: Inverted Residuals and Linear Bottlenecks" <https://arxiv.org/abs/1801.04381>`_.

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
            progress (bool): If True, displays a progress bar of the download to stderr
        """
        model = MobileNetV2(**kwargs)
        if pretrained:
            state_dict = PretrainedModelFactory._load_state_dict_from_url_with_retry(
                PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.MOBILENET_V2], progress=progress)
            model.load_state_dict(state_dict)
        return model

    @staticmethod
    def se_resnext50_32x4d(num_classes: int = 1000, pretrained: bool = True, pretrained_on: str = 'imagenet') -> SENet:
        """
        Constructs a se_resnext50_32x4d pretrained model.
        """
        model = SENet(SEResNeXtBottleneck, [3, 4, 6, 3], groups=32, reduction=16,
                      dropout_p=None, inplanes=64, input_3x3=False,
                      downsample_kernel_size=1, downsample_padding=0,
                      num_classes=num_classes)
        if pretrained:
            settings = pretrained_settings[PretrainedModelNames.SE_RESNEXT50_32X4D][pretrained_on]
            settings['url'] = PretrainedModelUrls.MODEL_URLS[PretrainedModelNames.SE_RESNEXT50_32X4D]
            PretrainedModelFactory._initialize_pretrained_model(model, num_classes, settings)
        return model

    @staticmethod
    def _vit(model_name: str, pretrained_model_name: str, num_classes: int = 1000, pretrained: bool = False,
             img_size: int = 224, progress: bool = True) -> VisionTransformer:
        r"""Helper methods to create vit models.

        :param model_name: Model name to pass to create_model()
        :type model_name: str
        :param pretrained_model_name: Pretrained model name
        :type pretrained_model_name: PretrainedModelNames
        :param num_classes: num_classes to pass to model
        :type num_classes: int
        :param pretrained: If True, returns a model pre-trained on ImageNet
        :type pretrained: bool
        :param img_size: Image size
        :type img_size: int
        :param progress: If True, displays a progress bar of the download to stderr
        :type progress: bool
        :return: vision transformer instance (vitb16r224)
        :rtype: VisionTransformer
        """
        model = create_model(model_name, pretrained=False, num_classes=num_classes, img_size=img_size)
        if pretrained:
            state_dict = PretrainedModelFactory._load_state_dict_from_url_with_retry(
                PretrainedModelUrls.MODEL_URLS[pretrained_model_name], progress=progress)
            # To resize pos embedding when using model at different img_size from pretrained weights
            state_dict = checkpoint_filter_fn(state_dict, model)
            del state_dict['head.weight'], state_dict['head.bias']
            model.load_state_dict(state_dict, strict=False)
        return model

    @staticmethod
    def vitb16r224(num_classes: int = 1000, pretrained: bool = False, img_size: int = 224,
                   progress: bool = True) -> VisionTransformer:
        r"""ViT-b16-r224 model from
        `"An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale"
            <https://arxiv.org/abs/2010.11929>`_.

        :param num_classes: num_classes to pass to model
        :type num_classes: int
        :param pretrained: If True, returns a model pre-trained on ImageNet
        :type pretrained: bool
        :param img_size: Image size
        :type img_size: int
        :param progress: If True, displays a progress bar of the download to stderr
        :type progress: bool
        :return: vision transformer instance (vitb16r224)
        :rtype: VisionTransformer
        """
        return PretrainedModelFactory._vit(model_name="vit_base_patch16_224",
                                           pretrained_model_name=PretrainedModelNames.VITB16R224,
                                           num_classes=num_classes,
                                           pretrained=pretrained,
                                           img_size=img_size,
                                           progress=progress)

    @staticmethod
    def vits16r224(num_classes: int = 1000, pretrained: bool = False, img_size: int = 224,
                   progress: bool = True) -> VisionTransformer:
        r"""ViT-s16-r224 model from
        `"How to train your ViT? Data, Augmentation, and Regularization in Vision Transformers"
            <https://arxiv.org/pdf/2106.10270.pdf>`_.

        :param num_classes: num_classes to pass to model
        :type num_classes: int
        :param pretrained: If True, returns a model pre-trained on ImageNet
        :type pretrained: bool
        :param img_size: Image size
        :type img_size: int
        :param progress: If True, displays a progress bar of the download to stderr
        :type progress: bool
        :return: vision transformer instance (vits16r224)
        :rtype: VisionTransformer
        """
        return PretrainedModelFactory._vit(model_name="vit_small_patch16_224",
                                           pretrained_model_name=PretrainedModelNames.VITS16R224,
                                           num_classes=num_classes,
                                           pretrained=pretrained,
                                           img_size=img_size,
                                           progress=progress)

    @staticmethod
    def vitl16r224(num_classes: int = 1000, pretrained: bool = False, img_size: int = 224,
                   progress: bool = True) -> VisionTransformer:
        r"""ViT-l16-r224 model from
        `"How to train your ViT? Data, Augmentation, and Regularization in Vision Transformers"
            <https://arxiv.org/pdf/2106.10270.pdf>`_.

        :param num_classes: num_classes to pass to model
        :type num_classes: int
        :param pretrained: If True, returns a model pre-trained on ImageNet
        :type pretrained: bool
        :param img_size: Image size
        :type img_size: int
        :param progress: If True, displays a progress bar of the download to stderr
        :type progress: bool
        :return: vision transformer instance (vitl16r224)
        :rtype: VisionTransformer
        """
        return PretrainedModelFactory._vit(model_name="vit_large_patch16_224",
                                           pretrained_model_name=PretrainedModelNames.VITL16R224,
                                           num_classes=num_classes,
                                           pretrained=pretrained,
                                           img_size=img_size,
                                           progress=progress)

    @staticmethod
    def _setup_resnet_fpn_backbone_model(model_constructor: torch.nn.Module, pretrained_model_name: str,
                                         backbone_name: str, pretrained: bool, progress: bool, num_classes: int,
                                         pretrained_backbone: bool, load_pretrained_model_dict: bool, strict: bool,
                                         backbone_kwargs: Dict[str, Any], **kwargs: Any) -> torch.nn.Module:

        # Check that number of classes is compatible with pretrained model.

        if pretrained and strict and num_classes != 91:
            raise AutoMLVisionSystemException(
                "Pretrained model is set to true and num_classes "
                "is set to {}, which is different from supported value 91.".format(num_classes))

        if pretrained:
            # no need to download the backbone if pretrained is set
            pretrained_backbone = False

        backbone = PretrainedModelFactory.resnet_fpn_backbone(backbone_name,
                                                              pretrained_backbone, **backbone_kwargs)

        model = model_constructor(backbone, num_classes, **kwargs)
        if pretrained and load_pretrained_model_dict:
            # Note the eventual load_state_dict_from_url method already uses SHA256 hash to ensure the unique
            # file name and check the file content.
            state_dict = PretrainedModelFactory._load_state_dict_from_url_with_retry(
                PretrainedModelUrls.MODEL_URLS[pretrained_model_name],
                progress=progress)

            if not strict:
                state_dict = intersect_dicts(state_dict, model.state_dict())
                if len(state_dict.keys()) == 0:
                    raise AutoMLVisionSystemException(
                        "Could not load pretrained model weights. State dict intersection is empty.", has_pii=False)
            model.load_state_dict(state_dict, strict=strict)

        return model

    @staticmethod
    def fasterrcnn_resnet18_fpn(pretrained: bool = False, progress: bool = True,
                                num_classes: int = 91, pretrained_backbone: bool = True,
                                load_pretrained_model_dict: bool = True, **kwargs: Any) -> FasterRCNN:

        '''
        Constructs a Faster R-CNN model with a ResNet-18-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        '''
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            FasterRCNN,
            PretrainedModelNames.FASTERRCNN_RESNET18_FPN_COCO,
            PretrainedModelNames.RESNET18,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def fasterrcnn_resnet34_fpn(pretrained: bool = False, progress: bool = True,
                                num_classes: int = 91, pretrained_backbone: bool = True,
                                load_pretrained_model_dict: bool = True, **kwargs: Any) -> FasterRCNN:

        '''
        Constructs a Faster R-CNN model with a ResNet-34-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        '''
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            FasterRCNN,
            PretrainedModelNames.FASTERRCNN_RESNET34_FPN_COCO,
            PretrainedModelNames.RESNET34,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def fasterrcnn_resnet50_fpn(pretrained: bool = False, progress: bool = True,
                                num_classes: int = 91, pretrained_backbone: bool = True,
                                load_pretrained_model_dict: bool = True, **kwargs: Any) -> FasterRCNN:
        """
        Constructs a Faster R-CNN model with a ResNet-50-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            FasterRCNN,
            PretrainedModelNames.FASTERRCNN_RESNET50_FPN_COCO,
            PretrainedModelNames.RESNET50,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def fasterrcnn_resnet101_fpn(pretrained: bool = False, progress: bool = True,
                                 num_classes: int = 91, pretrained_backbone: bool = True,
                                 load_pretrained_model_dict: bool = True, **kwargs: Any) -> FasterRCNN:
        """
        Constructs a Faster R-CNN model with a ResNet-101-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            FasterRCNN,
            PretrainedModelNames.FASTERRCNN_RESNET101_FPN_COCO,
            PretrainedModelNames.RESNET101,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def fasterrcnn_resnet152_fpn(pretrained: bool = False, progress: bool = True,
                                 num_classes: int = 91, pretrained_backbone: bool = True,
                                 load_pretrained_model_dict: bool = True, **kwargs: Any) -> FasterRCNN:
        """
        Constructs a Faster R-CNN model with a ResNet-152-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            FasterRCNN,
            PretrainedModelNames.FASTERRCNN_RESNET152_FPN_COCO,
            PretrainedModelNames.RESNET152,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def maskrcnn_resnet18_fpn(pretrained: bool = False, progress: bool = True,
                              num_classes: int = 91, pretrained_backbone: bool = True,
                              load_pretrained_model_dict: bool = True, **kwargs: Any) -> MaskRCNN:
        """
        Constructs a Mask R-CNN model with a ResNet-18-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            MaskRCNN,
            PretrainedModelNames.MASKRCNN_RESNET18_FPN_COCO,
            PretrainedModelNames.RESNET18,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def maskrcnn_resnet34_fpn(pretrained: bool = False, progress: bool = True,
                              num_classes: int = 91, pretrained_backbone: bool = True,
                              load_pretrained_model_dict: bool = True, **kwargs: Any) -> MaskRCNN:
        """
        Constructs a Mask R-CNN model with a ResNet-34-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            MaskRCNN,
            PretrainedModelNames.MASKRCNN_RESNET34_FPN_COCO,
            PretrainedModelNames.RESNET34,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def maskrcnn_resnet50_fpn(pretrained: bool = False, progress: bool = True,
                              num_classes: int = 91, pretrained_backbone: bool = True,
                              load_pretrained_model_dict: bool = True, **kwargs: Any) -> MaskRCNN:
        """
        Constructs a Mask R-CNN model with a ResNet-50-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            MaskRCNN,
            PretrainedModelNames.MASKRCNN_RESNET50_FPN_COCO,
            PretrainedModelNames.RESNET50,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def maskrcnn_resnet101_fpn(pretrained: bool = False, progress: bool = True,
                               num_classes: int = 91, pretrained_backbone: bool = True,
                               load_pretrained_model_dict: bool = True, **kwargs: Any) -> MaskRCNN:
        """
        Constructs a Mask R-CNN model with a ResNet-101-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            MaskRCNN,
            PretrainedModelNames.MASKRCNN_RESNET101_FPN_COCO,
            PretrainedModelNames.RESNET101,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def maskrcnn_resnet152_fpn(pretrained: bool = False, progress: bool = True,
                               num_classes: int = 91, pretrained_backbone: bool = True,
                               load_pretrained_model_dict: bool = True, **kwargs: Any) -> MaskRCNN:
        """
        Constructs a Mask R-CNN model with a ResNet-101-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            MaskRCNN,
            PretrainedModelNames.MASKRCNN_RESNET152_FPN_COCO,
            PretrainedModelNames.RESNET152,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict, strict=True,
            backbone_kwargs={}, **kwargs)

    @staticmethod
    def retinanet_restnet50_fpn(pretrained: bool = False, progress: bool = True,
                                num_classes: int = 91, pretrained_backbone: bool = True,
                                load_pretrained_model_dict: bool = True, **kwargs: Any) -> RetinaNet:
        """
        Constructs a RetinaNet model with a RestNet-50-FPN backbone.

        Args:
            pretrained (bool): If True, returns a model pre-trained on COCO train2017.
            progress (bool): If True, displays a progress bar of the download to stderr.
            num_classes: Number of classes.
            pretrained_backbone: Pretrained backbone.
            load_pretrained_model_dict: Load pretrained weights for entire model.
        """
        if num_classes is None:
            num_classes = 91
        # skip P2 because it generates too many anchors (according to their paper)
        backbone_kwargs = {
            "returned_layers": [2, 3, 4],
            "extra_blocks": LastLevelP6P7(256, 256)
        }
        # When num_classes is not default (91), there is difference in shape of keys
        # (from num_classes dependent nodes) in state dict of pretrained model and current model.
        # Skip those keys while loading pretrained model weights.
        strict = (num_classes == 91)
        return PretrainedModelFactory._setup_resnet_fpn_backbone_model(
            RetinaNet,
            PretrainedModelNames.RETINANET_RESNET50_FPN_COCO,
            PretrainedModelNames.RESNET50,
            pretrained, progress, num_classes, pretrained_backbone,
            load_pretrained_model_dict,
            strict=strict,
            backbone_kwargs=backbone_kwargs, **kwargs)

    @staticmethod
    def resnet_fpn_backbone(backbone_name: str, pretrained: bool,
                            norm_layer: torch.nn.Module = misc_nn_ops.FrozenBatchNorm2d,
                            trainable_layers: int = 3,
                            returned_layers: Optional[List[int]] = None,
                            extra_blocks: Optional[torch.nn.Module] = None) -> BackboneWithFPN:
        """Get the resnet fpn backbone."""
        backbone = getattr(PretrainedModelFactory, backbone_name)(pretrained=pretrained,
                                                                  norm_layer=norm_layer)

        # select layers that wont be frozen
        assert trainable_layers <= 5 and trainable_layers >= 0
        layers_to_train = ['layer4', 'layer3', 'layer2', 'layer1', 'conv1'][:trainable_layers]
        # freeze layers only if pretrained backbone is used
        for name, parameter in backbone.named_parameters():
            if all([not name.startswith(layer) for layer in layers_to_train]):
                parameter.requires_grad_(False)

        if extra_blocks is None:
            extra_blocks = LastLevelMaxPool()

        if returned_layers is None:
            returned_layers = [1, 2, 3, 4]
        assert min(returned_layers) > 0 and max(returned_layers) < 5
        return_layers = {f'layer{k}': str(v) for v, k in enumerate(returned_layers)}

        in_channels_stage2 = backbone.inplanes // 8
        in_channels_list = [in_channels_stage2 * 2 ** (i - 1) for i in returned_layers]
        out_channels = 256
        return BackboneWithFPN(backbone, return_layers, in_channels_list, out_channels, extra_blocks=extra_blocks)

    @staticmethod
    def _resnet(arch: str, block: torch.nn.Module, layers: List[int],
                pretrained: bool, progress: bool, **kwargs: Any) -> torch.nn.Module:
        model = ResNet(block, layers, **kwargs)
        if pretrained:
            # Note the eventual load_state_dict_from_url method already uses SHA256 hash to ensure the unique
            # file name and check the file content.
            state_dict = PretrainedModelFactory._load_state_dict_from_url_with_retry(
                PretrainedModelUrls.MODEL_URLS[arch], progress=progress)
            model.load_state_dict(state_dict)
        return model

    @staticmethod
    def _initialize_pretrained_model(model: torch.nn.Module, num_classes: int, settings: Dict[str, Any]) -> None:
        assert num_classes == settings['num_classes'], \
            'num_classes should be {}, but is {}'.format(
                settings['num_classes'], num_classes)
        state_dict = PretrainedModelFactory._load_state_dict_from_url_with_retry(settings['url'])
        model.load_state_dict(state_dict)
        model.input_space = settings['input_space']
        model.input_size = settings['input_size']
        model.input_range = settings['input_range']
        model.mean = settings['mean']
        model.std = settings['std']
