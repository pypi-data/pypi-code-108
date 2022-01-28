from deepomatic.oef.configs.config_utils import DataType, ModelConfig

from ..backbones import Backbones as bb

efficientdet = ModelConfig(
    display_name='EfficientDet',
    meta_arch='efficientdet',
    args={
        '@meta_arch': {
            'aspect_ratios': [{'height_ratio': 1., 'width_ratio': 1.}, {'height_ratio': 1.4, 'width_ratio': 0.7}, {'height_ratio': 0.7, 'width_ratio': 1.4}]
        },
        '@model.backbone.input.data_augmentation_options': [{'random_horizontal_flip': {'keypoint_flip_permutation': []}}],
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B0,
    model_display_name="EfficientDet D0 - EfficientNet B0",
    model_aliases=['efficientdet_d0.efficientnet_b0'],
    args={
        'trainer': {
            'batch_size': 16,
            'initial_learning_rate': 0.002,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 512, 'width': 512, 'resize_method': 'BICUBIC'}},
        '@model.backbone.efficientnet.survival_prob': 0.,
        '@meta_arch.fpn_num_filters': 64,
        '@meta_arch.fpn_cell_repeats': 3,
        '@meta_arch.box_class_repeats': 3,
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d0.tar.gz',
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B1,
    model_display_name="EfficientDet D1 - EfficientNet B1",
    model_aliases=['efficientdet_d1.efficientnet_b1'],
    args={
        'trainer': {
            'batch_size': 8,
            'initial_learning_rate': 0.002,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 640, 'width': 640, 'resize_method': 'BICUBIC'}},
        '@meta_arch.fpn_num_filters': 88,
        '@meta_arch.fpn_cell_repeats': 4,
        '@meta_arch.box_class_repeats': 3,
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d1.tar.gz',
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B2,
    model_display_name="EfficientDet D2 - EfficientNet B2",
    model_aliases=['efficientdet_d2.efficientnet_b2'],
    args={
        'trainer': {
            'batch_size': 4,
            'initial_learning_rate': 0.002,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 768, 'width': 768, 'resize_method': 'BICUBIC'}},
        '@meta_arch.fpn_num_filters': 112,
        '@meta_arch.fpn_cell_repeats': 5,
        '@meta_arch.box_class_repeats': 3,
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d2.tar.gz',
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B3,
    model_display_name="EfficientDet D3 - EfficientNet B3",
    model_aliases=['efficientdet_d3.efficientnet_b3'],
    args={
        'trainer': {
            'batch_size': 2,
            'initial_learning_rate': 0.002,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 896, 'width': 896, 'resize_method': 'BICUBIC'}},
        '@meta_arch.fpn_num_filters': 160,
        '@meta_arch.fpn_cell_repeats': 6,
        '@meta_arch.box_class_repeats': 4,
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d3.tar.gz',
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B4,
    model_display_name="EfficientDet D4 - EfficientNet B4",
    model_aliases=['efficientdet_d4.efficientnet_b4'],
    args={
        'trainer': {
            'batch_size': 1,
            'initial_learning_rate': 0.004,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 1024, 'width': 1024, 'resize_method': 'BICUBIC'}},
        '@meta_arch.fpn_num_filters': 224,
        '@meta_arch.fpn_cell_repeats': 7,
        '@meta_arch.box_class_repeats': 4,
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d4.tar.gz',
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B5,
    model_display_name="EfficientDet D5 - EfficientNet B5",
    model_aliases=['efficientdet_d5.efficientnet_b5'],
    args={
        'trainer': {
            'batch_size': 1,
            'initial_learning_rate': 0.004,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 1280, 'width': 1280, 'resize_method': 'BICUBIC'}},
        '@meta_arch.fpn_num_filters': 288,
        '@meta_arch.fpn_cell_repeats': 7,
        '@meta_arch.box_class_repeats': 4,
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d5.tar.gz',
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B6,
    model_display_name="EfficientDet D6 - EfficientNet B6",
    model_aliases=['efficientdet_d6.efficientnet_b6'],
    args={
        'trainer': {
            'batch_size': 1,
            'initial_learning_rate': 0.004,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 1280, 'width': 1280, 'resize_method': 'BICUBIC'}},
        '@meta_arch.fpn_num_filters': 384,
        '@meta_arch.fpn_cell_repeats': 8,
        '@meta_arch.box_class_repeats': 5,
        '@meta_arch.fpn_name': 'bifpn_sum',
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d6.tar.gz',
    }
)
efficientdet.add_backbone(
    bb.EFFICIENTNET_B6,
    model_display_name="EfficientDet D7 - EfficientNet B6",
    model_aliases=['efficientdet_d7.efficientnet_b6'],
    args={
        'trainer': {
            'batch_size': 1,
            'initial_learning_rate': 0.004,
        },
        '@model.backbone.input.image_resizer': {'fixed_shape_resizer': {'height': 1536, 'width': 1536, 'resize_method': 'BICUBIC'}},
        '@meta_arch.fpn_num_filters': 384,
        '@meta_arch.fpn_cell_repeats': 8,
        '@meta_arch.box_class_repeats': 5,
        '@meta_arch.fpn_name': 'bifpn_sum',
    }, pretrained_parameters={
        DataType.NATURAL_RGB: 'tensorflow/natural_rgb/efficientdet-d7.tar.gz',
    }
)


configs = [efficientdet]
