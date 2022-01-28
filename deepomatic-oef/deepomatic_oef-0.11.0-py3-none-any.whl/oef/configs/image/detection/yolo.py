from deepomatic.oef.configs.config_utils import DataType, ModelConfig

from ..utils import fixed_shape_resizer
from ..backbones import Backbones as bb

yolo_v2 = ModelConfig(
    display_name='YOLO v2',
    meta_arch='yolo_v2',
    args={
        'trainer': {
            'batch_size': 64,
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(416, 416),
            'data_augmentation_options': [],
        },
        '@meta_arch.parameters': {
            'subdivisions': 16,
            'classification_loss': {'weighted_softmax': {'logit_scale': 1.0}}
        },

    },
)
yolo_v2.add_backbone(bb.DARKNET_19, args={'trainer': {'initial_learning_rate': 0.002}}, pretrained_parameters={
    DataType.NATURAL_RGB: 'darknet/natural_rgb/darknet19-yolo-voc2007.weights',
})

yolo_v3 = ModelConfig(
    display_name='YOLO v3',
    meta_arch='yolo_v3',
    args={
        'trainer': {
            'batch_size': 64,
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(416, 416),
            'data_augmentation_options': [],
        },
        '@meta_arch.parameters': {
            'subdivisions': 32,
            'classification_loss': {'weighted_sigmoid': {}}
        },
    },
)
yolo_v3.add_backbone(bb.DARKNET_53, args={'trainer': {'initial_learning_rate': 0.01}}, pretrained_parameters={
    DataType.NATURAL_RGB: 'darknet/natural_rgb/darknet53-yolo-imagenet2012.weights',
})

yolo_v3_spp = ModelConfig(
    display_name='YOLO v3 SPP',
    meta_arch='yolo_v3_spp',
    args={
        'trainer': {
            'batch_size': 64,
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(608, 608),
            'data_augmentation_options': [],
        },
        '@meta_arch.parameters': {
            'subdivisions': 16,
            'classification_loss': {'weighted_sigmoid': {}}
        },
    },
)
yolo_v3_spp.add_backbone(bb.DARKNET_53, args={'trainer': {'initial_learning_rate': 0.001}}, pretrained_parameters={
    DataType.NATURAL_RGB: 'darknet/natural_rgb/darknet53-yolo_v3_spp_608-coco.weights',
})


configs = [yolo_v2, yolo_v3, yolo_v3_spp]
