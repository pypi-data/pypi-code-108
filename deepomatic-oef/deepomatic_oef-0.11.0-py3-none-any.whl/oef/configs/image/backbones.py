from enum import Enum
from deepomatic.oef.configs.config_utils import DataType, BackboneConfig


class Backbones(Enum):
    DARKNET_19 = BackboneConfig("Darknet 19", {'darknet': {'depth': 19}}, {})
    DARKNET_53 = BackboneConfig("Darknet 53", {'darknet': {'depth': 53}}, {})

    EFFICIENTNET_B0 = BackboneConfig("EfficientNet B0", {'efficientnet': {'version': 0}, 'width_multiplier': 1.0}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b0_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B1 = BackboneConfig("EfficientNet B1", {'efficientnet': {'version': 1}, 'width_multiplier': 1.0}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b1_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B2 = BackboneConfig("EfficientNet B2", {'efficientnet': {'version': 2}, 'width_multiplier': 1.1}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b2_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B3 = BackboneConfig("EfficientNet B3", {'efficientnet': {'version': 3}, 'width_multiplier': 1.2}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b3_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B4 = BackboneConfig("EfficientNet B4", {'efficientnet': {'version': 4}, 'width_multiplier': 1.4}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b4_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B5 = BackboneConfig("EfficientNet B5", {'efficientnet': {'version': 5}, 'width_multiplier': 1.6}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b5_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B6 = BackboneConfig("EfficientNet B6", {'efficientnet': {'version': 6}, 'width_multiplier': 1.8}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b6_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B7 = BackboneConfig("EfficientNet B7", {'efficientnet': {'version': 7}, 'width_multiplier': 2.0}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b7_noisy_student-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_B8 = BackboneConfig("EfficientNet B8", {'efficientnet': {'version': 8}, 'width_multiplier': 2.2}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_b8_advprop-classification-imagenet2012-2017.tar.gz'
    })
    EFFICIENTNET_L2 = BackboneConfig("EfficientNet L2", {'efficientnet': {'version': 10}, 'width_multiplier': 4.3}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientnet_l2_noisy_student-classification-imagenet2012-2017.tar.gz'
    })

    INCEPTION_RESNET_V2 = BackboneConfig("Inception ResNet v2", {'inception_resnet': {'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/inception_resnet_v2-classification-imagenet2012-2016_08_30.ckpt'
    })

    INCEPTION_V1 = BackboneConfig("Inception v1", {'inception': {'version': 1}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/inception_v1-classification-imagenet2012-2016_08_28.ckpt'
    })
    INCEPTION_V2 = BackboneConfig("Inception v2", {'inception': {'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/inception_v2-classification-imagenet2012-2016_08_28.ckpt'
    })
    INCEPTION_V3 = BackboneConfig("Inception v3", {'inception': {'version': 3}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/inception_v3-classification-imagenet2012-2016_08_28.ckpt'
    })
    INCEPTION_V4 = BackboneConfig("Inception v4", {'inception': {'version': 4}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/inception_v4-classification-imagenet2012-2016_09_09.ckpt'
    })

    MOBILENET_V1 = BackboneConfig("MobileNet v1", {'mobilenet': {'version': 1}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v1-classification-imagenet2012-2018_02_22.tar.gz'
    })
    MOBILENET_V1_025 = BackboneConfig("MobileNet v1 25%", {'mobilenet': {'version': 1}, 'width_multiplier': 0.25}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v1_025-classification-imagenet2012-2018_02_22.tar.gz'
    }, alias='mobilenet_v1_025')
    MOBILENET_V1_050 = BackboneConfig("MobileNet v1 50%", {'mobilenet': {'version': 1}, 'width_multiplier': 0.5}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v1_050-classification-imagenet2012-2018_02_22.tar.gz'
    }, alias='mobilenet_v1_050')
    MOBILENET_V1_075 = BackboneConfig("MobileNet v1 75%", {'mobilenet': {'version': 1}, 'width_multiplier': 0.75}, {}, alias='mobilenet_v1_075')
    MOBILENET_V2 = BackboneConfig("MobileNet v2", {'mobilenet': {'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v2-classification-imagenet2012-2018_03_28.tar.gz'
    })
    MOBILENET_V2_140 = BackboneConfig("MobileNet v2 140%", {'mobilenet': {'version': 2}, 'width_multiplier': 1.4}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v2_140-classification-imagenet2012-2018_03_28.tar.gz'
    }, alias='mobilenet_v2_140')

    NASNET_LARGE = BackboneConfig("NasNet Large", {'nasnet': {'depth': 0, 'version': 1}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/nasnet_large-classification-imagenet2012-2017_10_04.tar.gz'
    })
    NASNET_MOBILE = BackboneConfig("NasNet Mobile", {'nasnet': {'depth': 1, 'version': 1}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/nasnet_mobile-classification-imagenet2012-2017_10_04.tar.gz'
    })
    PNASNET_LARGE = BackboneConfig("PNasNet Large", {'nasnet': {'depth': 0, 'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/pnasnet_large-classification-imagenet2012-2017_12_13.tar.gz'
    })
    PNASNET_MOBILE = BackboneConfig("PNasNet Mobile", {'nasnet': {'depth': 1, 'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/pnasnet_mobile-classification-imagenet2012-2017_12_13.tar.gz'
    })

    RESNET_101_V1 = BackboneConfig("ResNet 101 v1", {'resnet': {'depth': 101, 'version': 1}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/resnet_101_v1-classification-imagenet2012-2016_08_28.ckpt'
    })
    RESNET_101_V2 = BackboneConfig("ResNet 101 v2", {'resnet': {'depth': 101, 'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/resnet_101_v2-classification-imagenet2012-2017_04_14.ckpt'
    })
    RESNET_152_V1 = BackboneConfig("ResNet 152 v1", {'resnet': {'depth': 152, 'version': 1}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/resnet_152_v1-classification-imagenet2012-2016_08_28.ckpt'
    })
    RESNET_152_V2 = BackboneConfig("ResNet 152 v2", {'resnet': {'depth': 152, 'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/resnet_152_v2-classification-imagenet2012-2017_04_14.ckpt'
    })
    RESNET_200_V1 = BackboneConfig("ResNet 200 v1", {'resnet': {'depth': 200, 'version': 1}}, {})
    RESNET_200_V2 = BackboneConfig("ResNet 200 v2", {'resnet': {'depth': 200, 'version': 2}}, {})
    RESNET_50_V1 = BackboneConfig("ResNet 50 v1", {'resnet': {'depth': 50, 'version': 1}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/resnet_50_v1-classification-imagenet2012-2016_08_28.ckpt'
    })
    RESNET_50_V2 = BackboneConfig("ResNet 50 v2", {'resnet': {'depth': 50, 'version': 2}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/resnet_50_v2-classification-imagenet2012-2017_04_14.ckpt'
    })

    VGG_11 = BackboneConfig("VGG 11", {'vgg': {'depth': 11}}, {})
    VGG_16 = BackboneConfig("VGG 16", {'vgg': {'depth': 16}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/vgg_16-classification-imagenet2012-2016_08_28.ckpt'
    })
    VGG_19 = BackboneConfig("VGG 19", {'vgg': {'depth': 19}}, {
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/vgg_19-classification-imagenet2012-2016_08_28.ckpt'
    })
