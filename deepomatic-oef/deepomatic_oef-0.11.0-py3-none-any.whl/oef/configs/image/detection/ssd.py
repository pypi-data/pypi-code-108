from deepomatic.oef.configs.utils import dict_inject
from deepomatic.oef.configs.config_utils import DataType, ModelConfig

from ..utils import fixed_shape_resizer
from ..backbones import Backbones as bb

feature_extractor_conv_hyperparams = {
    'activation': 'RELU_6',
    'batch_norm': {
        'center': True,
        'decay': 0.9997,
        'epsilon': 0.001,
        'scale': True,
        'train': True
    },
    'initializer': {
        'truncated_normal_initializer': {
            'mean': 0.0,
            'stddev': 0.03
        }
    },
    'op': 'CONV',
    'regularize_depthwise': False,
    'regularizer': {
        'l2_regularizer': {
            'weight': 0.00004
        }
    }
}

ssd_conv_hyperparams = {
    "activation": "RELU_6",
    "initializer": {
        "truncated_normal_initializer": {
            "mean": 0.0,
            "stddev": 0.03
        }
    },
    "op": "CONV",
    "regularize_depthwise": False,
    "regularizer": {
        "l2_regularizer": {
            "weight": 0.00004
        }
    }
}

ssd_lite_conv_hyperparams = {
    "activation": "RELU_6",
    "batch_norm": {
        "center": True,
        "decay": 0.9997,
        "epsilon": 0.001,
        "scale": True,
        "train": True
    },
    "initializer": {
        "truncated_normal_initializer": {
            "mean": 0.0,
            "stddev": 0.03
        }
    },
    "op": "CONV",
    "regularize_depthwise": False,
    "regularizer": {
        "l2_regularizer": {
            "weight": 0.00004
        }
    }
}

common_config = {
    'trainer': {
        'batch_size': 24,
    },
    '@model.backbone.input': {
        'image_resizer': fixed_shape_resizer(300, 300),
        'data_augmentation_options': [{'random_horizontal_flip': {'keypoint_flip_permutation': []}}],
    },
    '@meta_arch': {
        'anchor_generator': {
            'ssd_anchor_generator': {
                'aspect_ratios': [
                    1.0,
                    2.0,
                    0.5,
                    3.0,
                    0.3333
                ],
                'base_anchor_height': 1.0,
                'base_anchor_width': 1.0,
                'height_offset': [],
                'height_stride': [],
                'interpolated_scale_aspect_ratio': 1.0,
                'max_scale': 0.95,
                'min_scale': 0.2,
                'num_layers': 6,
                'reduce_boxes_in_lowest_layer': True,
                'scales': [],
                'width_offset': [],
                'width_stride': []
            }
        },
        'box_coder': {
            'faster_rcnn_box_coder': {
                'height_scale': 5.0,
                'width_scale': 5.0,
                'x_scale': 10.0,
                'y_scale': 10.0
            }
        },
        'box_predictor': {
            'convolutional_box_predictor': {
                'apply_sigmoid_to_scores': False,
                'box_code_size': 4,
                'class_prediction_bias_init': 0.0,
                'dropout_keep_probability': 0.8,
                'kernel_size': 3,
                'max_depth': 0,
                'min_depth': 0,
                'num_layers_before_predictor': 0,
                'use_dropout': False
            }
        },
        'matcher': {
            'argmax_matcher': {
                'force_match_for_each_row': True,
                'ignore_thresholds': False,
                'matched_threshold': 0.5,
                'negatives_lower_than_unmatched': True,
                'unmatched_threshold': 0.5,
                'use_matmul_gather': False
            }
        },
        'post_processing': {
            'batch_non_max_suppression': {
                'iou_threshold': 0.6,
                'max_detections_per_class': 100,
                'max_total_detections': 100,
                'score_threshold': 1e-8
            },
            'logit_scale': 1.0,
            'score_converter': 'SIGMOID'
        },
        'similarity_calculator': {
            'iou_similarity': {}
        },
        'losses': {
            'classification_weight': 1.,
            #  TODO: Add focal loss ?
            # 'classification_loss': {'weighted_sigmoid_focal': {'gamma': 2, 'alpha': 0.25}}
            # If we use the focal loss: we need to set hard_example_miner to 'None'
            'classification_loss': {'weighted_sigmoid': {}},
            'hard_example_miner': {
                'iou_threshold': 0.99,
                'loss_type': 'CLASSIFICATION',
                'max_negatives_per_positive': 3,
                'num_hard_examples': 3000
            },
            'localization_loss': {
                'weighted_smooth_l1': {
                    'anchorwise_output': False,
                    'delta': 1.0
                }
            },
            'localization_weight': 1.0
        },
        'feature_extractor': {
            'conv_hyperparams': feature_extractor_conv_hyperparams,
            'pad_to_multiple': 1,
            'use_explicit_padding': False
        },
    },
}

ssd = ModelConfig(
    display_name='SSD',
    meta_arch='ssd',
    args=dict_inject(common_config, {
        '@model.backbone.min_width': 16,
        '@meta_arch': {
            'box_predictor.convolutional_box_predictor': {
                'use_depthwise': False,
                'conv_hyperparams': ssd_conv_hyperparams,
            },
            'feature_extractor.use_depthwise': False,
        }
    }),
)
# TODO: Why not using 'min_negatives_per_image': 3 for everyone ?
ssd.add_backbone(bb.INCEPTION_V2, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 0, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    DataType.NATURAL_RGB: 'tensorflow/natural_rgb/inception_v2-ssd-coco-2018_01_28.tar.gz',
}),
ssd.add_backbone(bb.INCEPTION_V3, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 0, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}),
ssd.add_backbone(bb.MOBILENET_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 0, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v1-ssd-coco-2018_01_28.tar.gz',
}),
ssd.add_backbone(bb.MOBILENET_V2, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 3}, pretrained_parameters={
    DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v2-ssd-coco-2018_03_29.tar.gz',
}),
ssd.add_backbone(bb.RESNET_50_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 0, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    # See: https://github.com/Deepomatic/thoth/issues/277
    # DataType.NATURAL_RGB: 'tensorflow/natural_rgb/resnet_50_v1_fpn-ssd-coco-2018_07_03.tar.gz',
}),
ssd.add_backbone(bb.RESNET_101_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 0, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}),
ssd.add_backbone(bb.RESNET_152_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 0, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}),
for backbone in bb:
    if backbone not in [bb.DARKNET_19, bb.DARKNET_53]:
        ssd.add_backbone(backbone, args={'trainer': {'initial_learning_rate': 0.004}, '@meta_arch.losses.hard_example_miner.min_negatives_per_image': 0, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, skip_existing_aliases=True)


ssd_light = ModelConfig(
    display_name='SSD Lite',
    meta_arch='ssd',
    args=dict_inject(common_config, {
        '@meta_arch': {
            'box_predictor.convolutional_box_predictor': {
                'use_depthwise': True,
                'conv_hyperparams': ssd_lite_conv_hyperparams,
            },
            'feature_extractor.use_depthwise': True,
            'losses.hard_example_miner.min_negatives_per_image': 3,
        }
    })
)
# We use DataType.NATURAL_RGB: None to deactivate those models for DataType.NATURAL_RGB. Question: is it necessary ?
ssd_light.add_backbone(bb.INCEPTION_V2, args={'trainer': {'initial_learning_rate': 0.004}, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    DataType.NATURAL_RGB: None,
})
ssd_light.add_backbone(bb.INCEPTION_V3, args={'trainer': {'initial_learning_rate': 0.004}, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    DataType.NATURAL_RGB: None,
})
ssd_light.add_backbone(bb.MOBILENET_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@model.backbone.min_width': 16}, pretrained_parameters={
    DataType.NATURAL_RGB: None,
})
ssd_light.add_backbone(bb.MOBILENET_V2, args={
    'trainer': {
        'initial_learning_rate': 0.004
    },
    '@model.backbone.min_width': 16,
    # TODO: should we use that ?
    # '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}
}, pretrained_parameters={
    DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mobilenet_v2-ssd_lite-coco-2018_05_09.tar.gz',
})
# ssd_light.add_backbone(bb.MOBILENET_V2, args={'trainer': {'initial_learning_rate': 0.004}, ),
ssd_light.add_backbone(bb.RESNET_50_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    DataType.NATURAL_RGB: None,
}),
ssd_light.add_backbone(bb.RESNET_101_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    DataType.NATURAL_RGB: None,
}),
ssd_light.add_backbone(bb.RESNET_152_V1, args={'trainer': {'initial_learning_rate': 0.004}, '@model.backbone.hyperparameters': feature_extractor_conv_hyperparams}, pretrained_parameters={
    DataType.NATURAL_RGB: None,
}),


configs = [ssd, ssd_light]
