# Based on https://github.com/tensorflow/models/blob/master/research/object_detection/samples/configs/mask_rcnn_resnet101_atrous_coco.config
from ..backbones import Backbones as bb
from ..utils import keep_aspect_ratio_resizer
from deepomatic.oef.configs.config_utils import DataType, ModelConfig

# Define a meta arch for segmentation which USES faster_rcnn
mask_rcnn = ModelConfig(
    display_name='Mask RCNN',
    meta_arch='mask_rcnn',
    args={
        'trainer': {
            'batch_size': 1,
        },
        '@meta_arch': {
            'initial_crop_size': 14,
            'maxpool_kernel_size': 2,
            'maxpool_stride': 2,
        },
        '@model.backbone.input': {
            # (700, 1000) is the highest resolution found to work on 16gb GPU memory
            # A lower resolution linearly improves the speed of training, but it probably decreases the quality of the model
            'image_resizer': keep_aspect_ratio_resizer(700, 1000),
        },
        '@meta_arch.parameters': {
            'number_of_stages': 3,
            'first_stage_anchor_generator': {
                'grid_anchor_generator': {
                    'aspect_ratios': [
                        0.5,
                        1.0,
                        2.0
                    ],
                    'height_stride': 16,
                    'scales': [
                        0.25,
                        0.5,
                        1.0,
                        2.0
                    ],
                    'width_stride': 16
                }
            },
            'first_stage_atrous_rate': 2,
            'first_stage_box_predictor_conv_hyperparams': {
                'op': 'CONV',
                'initializer': {
                    'truncated_normal_initializer': {
                        'stddev': 0.01
                    }
                },
                'regularizer': {
                    'l2_regularizer': {
                        'weight': 0.0
                    }
                }
            },
            'first_stage_nms_score_threshold': 0.0,
            'first_stage_nms_iou_threshold': 0.7,
            'first_stage_max_proposals': 300,
            'first_stage_localization_loss_weight': 2.0,
            'first_stage_objectness_loss_weight': 1.0,
            # Can be 8 (default maskrcnn) or 16 (maskrcnn for pets, faster rcnn). Modify height_stride and width_stride too
            # A stride of 16 allows 75% more steps/sec for the same precision
            'first_stage_features_stride': 16,

            'second_stage_box_predictor': {
                'mask_rcnn_box_predictor': {
                    'use_dropout': False,
                    'dropout_keep_probability': 1.0,
                    'predict_instance_masks': True,
                    'mask_height': 33,
                    'mask_width': 33,
                    'mask_prediction_conv_depth': 0,
                    'mask_prediction_num_conv_layers': 4,
                    'fc_hyperparams': {
                        'op': 'FC',
                        'initializer': {
                            'variance_scaling_initializer': {
                                'factor': 1.0,
                                'mode': 'FAN_AVG',
                                'uniform': True
                            }
                        },
                        'regularize_depthwise': False,
                        'regularizer': {
                            'l2_regularizer': {
                                'weight': 0.0
                            }
                        }
                    },
                    'conv_hyperparams': {
                        'op': 'CONV',
                        'regularizer': {
                            'l2_regularizer': {
                                'weight': 0.0
                            }
                        },
                        'initializer': {
                            'truncated_normal_initializer': {
                                'stddev': 0.01
                            }
                        }
                    }
                }
            },
            'second_stage_post_processing': {
                'batch_non_max_suppression': {
                    'iou_threshold': 0.6,
                    'max_detections_per_class': 100,
                    'max_total_detections': 300,
                    'score_threshold': 0.0
                },
                'score_converter': 'SOFTMAX'
            },
            'second_stage_localization_loss_weight': 2.0,
            'second_stage_classification_loss_weight': 1.0,
            'second_stage_mask_prediction_loss_weight': 4.0,
            'second_stage_classification_loss': {'weighted_softmax': {'logit_scale': 1.0}},
        },
    },
)

mask_rcnn.add_backbone(bb.RESNET_101_V1, args={'trainer': {'initial_learning_rate': 0.0003}}, pretrained_parameters={
    DataType.NATURAL_RGB: 'tensorflow/natural_rgb/mask_rcnn_resnet101_atrous_coco_2018_01_28-patched.tar.gz'
})

configs = [mask_rcnn]
