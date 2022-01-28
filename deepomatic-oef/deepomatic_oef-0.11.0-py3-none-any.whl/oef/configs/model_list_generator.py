import os
import json
import copy

from deepomatic.oef.configs.model_args import ModelArguments
from deepomatic.oef.configs.utils import dict_inject

###############################################################################

import deepomatic.oef.configs.image.classification.configs as image_classification
import deepomatic.oef.configs.image.detection.rcnn as image_detection_rcnn
import deepomatic.oef.configs.image.detection.ssd as image_detection_ssd
import deepomatic.oef.configs.image.detection.yolo as image_detection_yolo
import deepomatic.oef.configs.image.detection.efficientdet as image_detection_efficientdet
import deepomatic.oef.configs.image.ocr.attention as image_ocr_attention
import deepomatic.oef.configs.image.segmentation.mask_rcnn as image_segmentation


def concatenate_configs(modules):
    configs = []
    for m in modules:
        configs += m.configs
    return configs


configs = {
    'image_classification': concatenate_configs([image_classification]),
    'image_detection': concatenate_configs([
        image_detection_rcnn,
        image_detection_ssd,
        image_detection_yolo,
        image_detection_efficientdet,
    ]),
    'image_ocr': concatenate_configs([image_ocr_attention]),
    'image_segmentation': concatenate_configs([image_segmentation]),
}

###############################################################################

DEFAULT_LEARNING_RATE_POLICY = {
    "manual_step_learning_rate": {
        "schedule": [
            {
                "learning_rate_factor": 0.1,
                "step_pct": 0.33
            },
            {
                "learning_rate_factor": 0.01,
                "step_pct": 0.66
            }
        ],
    }
}

DEFAULT_OPTIMIZER = {
    "momentum_optimizer": {
    },
}

# DEFAULT_OPTIMIZER = {
#     "rms_prop_optimizer": {
#     },
#     "use_moving_average": True
# }


###############################################################################

class ModelFamilies:
    def __init__(self):
        self._families = {}

    def add_family(self, family_name):
        f = ModelFamily(family_name)
        self._families[family_name] = f
        return f

    def dump(self, module_path=None):
        dumped_groups = {}
        for _, family in self._families.items():
            for key, model_args in family.to_dict().items():
                key_parts = key.split('.')
                group_name = ' - '.join([key_parts[0], key_parts[1]]).upper()
                if group_name not in dumped_groups:
                    dumped_groups[group_name] = {}
                dumped_groups[group_name][key] = model_args
        dumped_groups = list(dumped_groups.items())
        dumped_groups.sort()
        dumped_groups = ''.join([self._dump_group_(group_name, group) for group_name, group in dumped_groups])
        dumped_txt = """# This file has been generated with `make models`: DO NOT EDIT!
from deepomatic.oef.configs.model_args import ModelArguments

model_list = {\n""" + dumped_groups + "}\n"  # add trailing line
        dumped_txt = dumped_txt.replace('"@', '').replace('@"', '').replace('\\"', '"')

        if module_path is None:
            module_path = os.path.join(os.path.dirname(__file__), 'model_list.py')
        with open(module_path, 'w') as f:
            f.write(dumped_txt)

    def _dump_group_(self, group_name, group):
        txt = json.dumps(group, sort_keys=True, indent=4, separators=(',', ': '))
        lines = txt.split('\n')
        lines[0] = '    # ' + group_name
        lines[-2] += ','
        lines[-1] = '\n'
        return '\n'.join(lines)


class ModelFamily:

    def __init__(self, family_name):
        self._family_name = family_name
        self._models = {
        }

    @property
    def name(self):
        return self._family_name

    def to_dict(self):
        return {key: repr(model) for key, model in self._models.items()}

    def add_model(self, key, display_name, default_args, pretrained_parameters):
        self._add_model_('pretraining_none', key, display_name, default_args)
        for pretraining_key, path in pretrained_parameters.items():
            if path is None:
                continue
            self._add_model_with_pretrained_weights_(
                'pretraining_' + pretraining_key.value,
                key, display_name, default_args,
                path)

    def _add_model_with_pretrained_weights_(self, pretraining_type, key, display_name, default_args, pretrained_weights):
        default_args = dict_inject(copy.deepcopy(default_args), {
            'trainer': {
                'pretrained_parameters': pretrained_weights
            },
        })
        self._add_model_(pretraining_type, key, display_name, default_args)

    def _add_model_(self, pretraining_type, key, display_name, default_args):
        model_key = '{}.{}.{}'.format(self._family_name, pretraining_type, key)
        self._models[model_key] = ModelArguments(display_name, default_args)


###############################################################################

# Script to add a model family
common_default_args = {
    'trainer': {
        'learning_rate_policy': DEFAULT_LEARNING_RATE_POLICY,
        'optimizer': DEFAULT_OPTIMIZER
    }
}


def add_models_to_family(family, model_config):
    meta_arch = None
    if model_config.meta_arch is not None:
        meta_arch = model_config.meta_arch

    def update_args(args, new_args):
        nonlocal meta_arch
        return dict_inject(args, new_args, shortcuts={
            '@model': ['trainer', family.name],
            '@meta_arch': ['trainer', family.name, meta_arch],
        })

    print('Generating {} - {}'.format(family.name, model_config.display_name))

    default_args = {}
    default_args = update_args(default_args, common_default_args)
    if meta_arch is not None:
        # IMPORTANT: This sets the meta_arch one-of even if it has not field
        default_args = update_args(default_args, {'@model.{}'.format(meta_arch): {}})

    for variant in model_config.variants:
        print('Generating {}.{}:'.format(family.name, variant.alias))

        args = update_args(default_args, variant.args)
        family.add_model(
            variant.alias,
            variant.display_name,
            args,
            variant.pretrained_parameters
        )


###############################################################################

def generate(module_path=None):
    families = ModelFamilies()

    for family_name, family_config in configs.items():
        family = families.add_family(family_name)
        for model_config in family_config:
            add_models_to_family(
                family,
                model_config)

    families.dump(module_path)
