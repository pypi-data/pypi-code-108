import copy
from enum import Enum

from .utils import dict_inject


###############################################################################

def make_alias(name):
    """Encode a human readable name into a model key"""
    return name.replace('%', '').replace(' ', '_').replace('-', '_').lower()


###############################################################################

class ModelVariant:

    def __init__(self, display_name, alias, args, pretrained_parameters):
        """
        Configuration class for a backbone.

        Args:
            display_name (string): The name to display for humans.
            alias (string): A key used to refer to this model when generating model_list.py.
            args (dict): A dict passed the protobuf for initialization.
            pretrained_parameters (dict): A dict DataType -> "path/to/pretrained.tar.gz" or None
        """
        self._display_name = display_name
        self._args = args
        self._pretrained_parameters = pretrained_parameters if pretrained_parameters is not None else {}
        self._alias = make_alias(display_name) if alias is None else alias

    @property
    def display_name(self):
        return self._display_name

    @property
    def alias(self):
        return self._alias

    @property
    def args(self):
        return self._args

    @property
    def pretrained_parameters(self):
        return self._pretrained_parameters

    def update(self, args=None, pretrained_parameters=None):
        """
        Similar to the behavior of dict.update for args and pretrained_parameters.
        Returns an updated copy of the object instead of modifying it inplace.

        Args:
            args (dict): If not None: the new `args` will be injected into backbone.args using dict_inject.
            pretrained_parameters (dict): If not None, the default backbone.pretrained_parameters will be
                                          updated with that dict.

        Return:
            An updated copy of self.
        """
        if args is None:
            args = copy.deepcopy(self._args)
        else:
            args = dict_inject(self._args, args)

        pretrained = copy.deepcopy(self._pretrained_parameters)
        if pretrained_parameters is not None:
            pretrained.update(pretrained_parameters)

        return ModelVariant(display_name=self._display_name, alias=self._alias, args=args, pretrained_parameters=pretrained)


###############################################################################

class DataType(Enum):
    NATURAL_RGB = 'natural_rgb'


class BackboneConfig(ModelVariant):

    def __init__(self, display_name, args, pretrained_parameters=None, alias=None):
        """
        Configuration class for a backbone.

        Args:
            display_name: see ModelVariant for the detail
            args: see ModelVariant for the detail
            pretrained_parameters: see ModelVariant for the detail
            alias: see ModelVariant for the detail
        """
        if alias is None:
            alias = make_alias(display_name)

        # Args passed when building a backbone are relative to @model.backbone
        args = {'@model.backbone': args}

        super(BackboneConfig, self).__init__(display_name, alias, args, pretrained_parameters)


###############################################################################

class ModelConfig:

    def __init__(self, display_name, args, meta_arch=None, alias=None):
        """
        Configuration class for a backbone.

        Args:
            display_name (string): The name to display for humans
            args (dict): A dict passed to Backbone protobuf for its initialization
            backbones (list): A list of BackboneConfig
            meta_arch (string): Protobuf meta_arch to use when using '@meta_arch' in args.
            alias (string): A key used to refer to this backbone when generating model_list.py. If None,
                            an alias is inferred from the display_name.
        """
        self._display_name = display_name
        self._args = args
        self._meta_arch = meta_arch

        if alias is None:
            alias = make_alias(display_name)
        self._alias = alias

        self._variants = []
        self._variants_keys = set()

    @property
    def display_name(self):
        return self._display_name

    @property
    def variants(self):
        return self._variants

    @property
    def meta_arch(self):
        return self._meta_arch

    def add_backbone(self, backbone, model_display_name=None, model_aliases=None, args=None, pretrained_parameters=None, skip_existing_aliases=False):
        """
        Add a backbone to this model.

        Args:
            backbone (Backbones enum key): A backbone enum.
            model_display_name (str): If not None, it will override the default display name made of the
                                      concatenation of model and backbone display names.
            model_aliases (list): If not None, it will override the default alias made of the
                                      concatenation of model and backbone aliases.
            args: See BackboneConfig.update.
            pretrained_parameters: See BackboneConfig.update.
            skip_existing_aliases (bool): If True, if will ignore already inserted models, otherwise it will
                                          raise an error in case of duplicate.
        """
        backbone = backbone.value
        variant = backbone.update(args=args, pretrained_parameters=pretrained_parameters)

        if model_display_name is None:
            model_display_name = '{} - {}'.format(self._display_name, backbone.display_name)
        if model_aliases is None:
            model_aliases = ['{}.{}'.format(self._alias, backbone.alias)]

        for alias in model_aliases:
            if alias in self._variants_keys:
                if skip_existing_aliases:
                    continue
                else:
                    raise Exception("Duplicate alias: {}".format(alias))
            self._variants_keys.add(alias)
            self._variants.append(ModelVariant(
                display_name=model_display_name,
                alias=alias,
                args=dict_inject(self._args, variant.args),
                pretrained_parameters=variant.pretrained_parameters
            ))
