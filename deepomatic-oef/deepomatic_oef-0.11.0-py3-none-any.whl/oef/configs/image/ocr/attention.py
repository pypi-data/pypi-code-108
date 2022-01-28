from deepomatic.oef.configs.config_utils import DataType, ModelConfig

from ..utils import fixed_shape_resizer
from ..backbones import Backbones as bb

attention = ModelConfig(
    display_name='Attention OCR',
    alias='attention',
    meta_arch='attention',
    args={
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(102, 32),
            'data_augmentation_options': [],
        },
    }
)
attention.add_backbone(
    bb.INCEPTION_V3,
    args={
        'trainer': {
            'batch_size': 32,
            'initial_learning_rate': 0.01
        }
    },
    pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/inception_v3-classification-imagenet2012-2016_08_28.ckpt'
    }
)

attention.add_backbone(
    bb.EFFICIENTNET_B0,
    args={
        'trainer': {
            'batch_size': 32,
            'initial_learning_rate': 0.01
        },
        '@model.backbone.efficientnet.survival_prob': 0.,
    },
    pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d0.tar.gz'
    }
)

configs = [attention]
