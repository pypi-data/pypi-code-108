from deepomatic.oef.configs.utils import dict_inject
from deepomatic.oef.configs.config_utils import ModelConfig

from ..utils import fixed_shape_resizer
from ..backbones import Backbones as bb

backbones = [
    (bb.VGG_11, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}),
    (bb.VGG_16, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}),
    (bb.VGG_19, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.0025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}),
    (bb.INCEPTION_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.8}}),
    (bb.INCEPTION_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.0025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.8}}),
    (bb.INCEPTION_V3, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(299, 299)}, 'dropout_keep_prob': 0.8}}),
    (bb.INCEPTION_V4, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(299, 299)}, 'dropout_keep_prob': 0.8}}),
    (bb.INCEPTION_RESNET_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(299, 299)}, 'dropout_keep_prob': 0.8}}),
    (bb.RESNET_50_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),  # TODO: try with dropout ?
    (bb.RESNET_101_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.RESNET_152_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.RESNET_200_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.RESNET_50_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.RESNET_101_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.RESNET_152_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.0025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.RESNET_200_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.MOBILENET_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}),
    (bb.MOBILENET_V1_075, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}),
    (bb.MOBILENET_V1_050, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}),
    (bb.MOBILENET_V1_025, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}),
    (bb.MOBILENET_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),  # TODO: try with dropout ?
    (bb.MOBILENET_V2_140, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}),
    (bb.NASNET_MOBILE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}),
    (bb.NASNET_LARGE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(331, 331)}, 'dropout_keep_prob': 0.5}}),
    (bb.PNASNET_MOBILE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}),
    (bb.PNASNET_LARGE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(331, 331)}, 'dropout_keep_prob': 0.5}}),
    (bb.EFFICIENTNET_B0, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032, 'do_not_restore_variables': ['efficientnet-b0/head/conv2d/kernel:0']}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 224, 'width': 224, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.8}}),
    (bb.EFFICIENTNET_B1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 240, 'width': 240, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.8}}),
    (bb.EFFICIENTNET_B2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 260, 'width': 260, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.7}}),
    (bb.EFFICIENTNET_B3, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 300, 'width': 300, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.7}}),
    (bb.EFFICIENTNET_B4, {'trainer': {'batch_size': 16, 'initial_learning_rate': 0.016}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 380, 'width': 380, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.6}}),
    (bb.EFFICIENTNET_B5, {'trainer': {'batch_size': 8, 'initial_learning_rate': 0.008}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 456, 'width': 456, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.6}}),
    (bb.EFFICIENTNET_B6, {'trainer': {'batch_size': 4, 'initial_learning_rate': 0.004}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 528, 'width': 528, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}),
    (bb.EFFICIENTNET_B7, {'trainer': {'batch_size': 2, 'initial_learning_rate': 0.002}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 600, 'width': 600, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}),
    (bb.EFFICIENTNET_B8, {'trainer': {'batch_size': 1, 'initial_learning_rate': 0.001}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 672, 'width': 672, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}),
    (bb.EFFICIENTNET_L2, {'trainer': {'batch_size': 1, 'initial_learning_rate': 0.001}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 800, 'width': 800, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}),
]

common_args = {
    '@model.backbone.input.data_augmentation_options': [{'random_horizontal_flip': {'keypoint_flip_permutation': []}}],
}

softmax_classifier = ModelConfig(
    display_name='Softmax',
    args=dict_inject(common_args, {'@model.loss': {'weighted_softmax': {'logit_scale': 1.0}}}),
)
for backbone, args in backbones:
    softmax_classifier.add_backbone(backbone, args=args)

sigmoid_classifier = ModelConfig(
    display_name='Sigmoid',
    args=dict_inject(common_args, {'exclusive_labels': False, '@model.loss': {'weighted_sigmoid': {}}}),
)
for backbone, args in backbones:
    sigmoid_classifier.add_backbone(backbone, args=args)

configs = [softmax_classifier, sigmoid_classifier]
