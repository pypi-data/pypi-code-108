import string
import re

import deepomatic.oef.protos.models.image.backbones_pb2 as backbones_pb2

NOT_RE = re.compile(r'not\((.*)\)')
CONCAT_BEFORE_RE = re.compile(r'concat_before\((.*)\)')


class CustomFormatter(string.Formatter):

    def get_field(self, field_name, args, kwargs):
        value = getattr(args[0], field_name)
        if isinstance(value, float):
            value = round(value, 7)  # otherwise we would for example get 0.800000011920929 for 0.8
        return value, field_name

    def format_field(self, value, format_spec):
        if format_spec != '':
            for format_spec in format_spec.split(','):
                if NOT_RE.match(format_spec):
                    exclude_value = NOT_RE.match(format_spec).group(1)
                    if isinstance(value, str):
                        if value == exclude_value:
                            value = ''
                            break
                    elif isinstance(value, float):
                        if value == float(exclude_value):
                            value = ''
                            break
                    elif isinstance(value, int):
                        if value == int(exclude_value):
                            value = ''
                            break
                    continue
                elif CONCAT_BEFORE_RE.match(format_spec):
                    concat_value = CONCAT_BEFORE_RE.match(format_spec).group(1)
                    value = concat_value + str(value)
                elif format_spec == 'space':
                    value = ' ' + str(value)
                elif format_spec == 'lower':
                    value = value.lower()
                elif format_spec == 'higher':
                    value = value.higher()
                elif format_spec == 'title':
                    value = value.title()
                elif format_spec.startswith('backbones_pb2.'):
                    enum_class = backbones_pb2
                    for field in format_spec.split('.')[1:]:
                        enum_class = getattr(enum_class, field)
                    int_to_key = {v: k for k, v in enum_class.items()}
                    value = int_to_key[value]
                else:
                    value = super(CustomFormatter, self).format_field(value, format_spec)

        return super(CustomFormatter, self).format_field(value, '')


def switch_and_format(options, obj, oneof_name):
    which_oneof = obj.WhichOneof(oneof_name)
    if which_oneof not in options:
        raise Exception("Unexpected one-of value: '{}'".format(which_oneof))

    format_value = options[which_oneof]
    if callable(format_value):
        return format_value(obj)
    else:
        fmt = CustomFormatter()
        return fmt.format(format_value, getattr(obj, which_oneof))


def backbone_to_name(backbone):
    width_multiplier_str = ''
    if backbone.width_multiplier != 1:
        width_multiplier_str = ' {:.0%}'.format(backbone.width_multiplier)

    options = {
        'vgg':              'VGG {depth}',  # noqa: E241
        'inception':        'Inception v{version}',  # noqa: E241
        'inception_resnet': 'Inception ResNet v{version}',  # noqa: E241
        'resnet':           'ResNet {depth} v{version}',  # noqa: E241
        'mobilenet':        'MobileNet v{version}' + width_multiplier_str,  # noqa: E241
        'nasnet':           '{version:backbones_pb2.NasNetBackbone.Version} {depth:backbones_pb2.NasNetBackbone.Depth,title}',  # noqa: E241
        'darknet':          'Darknet {depth}',  # noqa: E241
        'efficientnet':     'EfficientNet {version:backbones_pb2.EfficientNetBackbone.Version}',  # noqa: E241
    }
    return switch_and_format(options, backbone, 'backbone_type')


def ssd_version(model):
    if model.ssd.box_predictor.WhichOneof('box_predictor_oneof') == 'convolutional_box_predictor' and \
       model.ssd.box_predictor.convolutional_box_predictor.use_depthwise and \
       model.ssd.feature_extractor.use_depthwise:
        return 'SSD Lite'
    return 'SSD'


def efficientdet_version(model):
    efficientdet_arch = {
        64: 'D0',
        88: 'D1',
        112: 'D2',
        160: 'D3',
        224: 'D4',
        288: 'D5',
    }
    fpn_num_filters = model.efficientdet.fpn_num_filters
    if fpn_num_filters in efficientdet_arch:
        return 'EfficientDet ' + efficientdet_arch[fpn_num_filters]
    if fpn_num_filters == 384:
        if model.backbone.input.image_resizer.WhichOneof('image_resizer_oneof') == 'fixed_shape_resizer':
            if model.backbone.input.image_resizer.fixed_shape_resizer.width == 1280:
                return 'EfficientDet D6'
            elif model.backbone.input.image_resizer.fixed_shape_resizer.width == 1536:
                return 'EfficientDet D7'
    return 'EfficientDet'


def experiment_to_display_name(experiment):
    model_type = experiment.trainer.WhichOneof('model_type')
    model = getattr(experiment.trainer, model_type)

    backbone_name = None  # if left like this, we will use the default backbone accessor, see below
    if model_type == 'image_classification':
        meta_arch_name = switch_and_format({
            'weighted_sigmoid':        'Sigmoid',  # noqa: E241
            'weighted_softmax':        'Softmax',  # noqa: E241
            'weighted_logits_softmax': 'Softmax',  # noqa: E241
            'bootstrapped_sigmoid':    'Bootstrapped Sigmoid',  # noqa: E241
            'weighted_sigmoid_focal':  'Focal Loss',  # noqa: E241
        }, model.loss, 'classification_loss')
    elif model_type == 'image_detection':
        meta_arch_name = switch_and_format({
            'faster_rcnn':  'Faster RCNN',  # noqa: E241
            'rfcn':         'RFCN',  # noqa: E241
            'ssd':          ssd_version,  # noqa: E241
            'yolo_v2':      'YOLO v2',  # noqa: E241
            'yolo_v3':      'YOLO v3',  # noqa: E241
            'yolo_v3_spp':  'YOLO v3 SPP',  # noqa: E241
            'efficientdet': efficientdet_version,  # noqa: E241
        }, model, 'meta_architecture_type')
    elif model_type == 'image_ocr':
        meta_arch_name = switch_and_format({
            'attention': 'Attention OCR',
        }, model, 'meta_architecture_type')
    elif model_type == 'image_segmentation':
        meta_arch_name = switch_and_format({
            'mask_rcnn': 'Mask RCNN',
        }, model, 'meta_architecture_type')
    else:
        raise Exception("Unexpected model type: '{}'".format(model_type))

    if backbone_name is None:
        backbone_name = backbone_to_name(model.backbone)

    return '{} - {}'.format(meta_arch_name, backbone_name)
