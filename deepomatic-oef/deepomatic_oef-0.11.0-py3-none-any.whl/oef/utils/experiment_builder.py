import copy
import logging
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
import google.protobuf.json_format as json_format

from deepomatic.oef.configs import model_list
from deepomatic.oef.utils.common import parse_protobuf_from_json_or_binary
from deepomatic.oef.utils.class_helpers import load_proto_class_from_protobuf_descriptor
from deepomatic.oef.protos.experiment_pb2 import Experiment
from deepomatic.oef.protos.hyperparameter_pb2 import field_option, oneof_option, HyperParameter

logger = logging.getLogger(__name__)


class InvalidNet(Exception):
    pass


class ExperimentBuilder(object):
    """
    This class can build a Experiment protobuf given the pre-determined parameters. You can also pass
    additionnal parameters to override the default arguments. In that purpose, all fields of Model and its
    sub-messages are assumed to have a different name (this assumpition is checked by model_generator).
    """

    _model_list = None

    def __init__(self, model_type_key):
        if self._model_list is None:
            self.load_model_list()
        if model_type_key not in self._model_list:
            # Try model_type_key reordering to provide backward compatibility with oef<0.5.0
            model_type_key_parts = model_type_key.split('.')
            model_type_key_new_format = '.'.join([model_type_key_parts[0], model_type_key_parts[-1]] + model_type_key_parts[1:-1])
            if model_type_key_new_format in self._model_list:
                logger.warning("This model key format is deprecated: '{}'. Use '{}' instead.".format(model_type_key, model_type_key_new_format))
                model_type_key = model_type_key_new_format
            else:
                raise InvalidNet("Unknown model key '{}'. Also tried '{}' for backward compatibility.".format(model_type_key, model_type_key_new_format))
        self._model_args = self._model_list[model_type_key]
        self._hyperparameters = {}

    @classmethod
    def load_model_list(cls):
        # Avoid to load it at the root of the module to avoid nested import loops
        cls._model_list = {}
        for key, args in model_list.model_list.items():
            assert key not in cls._model_list, "Duplicate model key, this should not happen"
            cls._model_list[key] = args

    def add_hyperparameter(self, hyperparameter, distribution=None):
        """
        Add a hyperparameter to the experiment.

        Args:
            hyperparameter (string): path to hyperparameter in the protobuf hierarchy seperated by a '.' (e.g., 'trainer.batch_size')
            distribution (dict, Message, JSON, binary): Hyperparameter distribution
        """
        def convert_to_protobuf(value):
            """
            Convert a dict / JSON / binary to protobuf Message
            """
            if isinstance(value, dict):
                value = json_format.ParseDict(value, HyperParameter())
            elif isinstance(value, Message):
                pass
            else:
                value = parse_protobuf_from_json_or_binary(HyperParameter, value)
            return value

        if hyperparameter == 'trainer.num_train_steps':
            raise Exception(f'`{hyperparameter}` is not available for hyperparameter optimization')

        if distribution is None:
            distribution = self._get_default_distribution_(Experiment, hyperparameter)
        else:
            self._recursive_search_(Experiment, hyperparameter)

        self._hyperparameters[hyperparameter] = convert_to_protobuf(distribution)

    @staticmethod
    def _get_default_distribution_(protobuf_class, hyperparameter):
        """
        Recursively find and fill default distribution for hyperparameter

        Args:
            protobuf_class (protobuf): parent protobuf class from which to start recursively the finding procedure
            hyperparameter (string): path to hyperparameter in the protobuf hierarchy seperated by a '.' (e.g., 'trainer.batch_size')
        """

        # Get field and protobuf class for the given hyperparameter
        protobuf_class, field_name = ExperimentBuilder._recursive_search_(protobuf_class, hyperparameter)

        # If the field_name is None, it is an OneOf
        if field_name is None:
            oneofs = protobuf_class.DESCRIPTOR.oneofs
            assert len(oneofs) == 1, f'Number of OneOfs should be 1, found {len(oneofs)}. This should not happen.'
            oneof = oneofs[0]
            if not oneof.has_options:
                raise Exception('No distribution given for hyperparemeter {}'.format(oneof.name))
            return oneof.GetOptions().Extensions[oneof_option]
        else:
            field = protobuf_class.DESCRIPTOR.fields_by_name[field_name]
            if field.message_type is None or field.label == FieldDescriptor.LABEL_REPEATED:
                if not field.has_options:
                    raise Exception('No distribution given for hyperparemeter {}'.format(field_name))
                return field.GetOptions().Extensions[field_option]

    @staticmethod
    def _recursive_search_(protobuf_class, path_name):
        """
        Check if path_name is correct by checking recursively fields of the input protobuf_class

        Args:
            protobuf_class (protobuf): parent protobuf class from which to start recursively the finding procedure
            hyperparameter (string): path to hyperparameter in the protobuf hierarchy seperated by a '.' (e.g., 'trainer.batch_size')

        Returns:
            protobuf, field_name tuple. field_name is None for OneOf
        """
        fields = path_name.split('.')

        # We walk down the parameter path recursively
        for i, field_name in enumerate(fields):
            # Check if the field exists
            if field_name not in protobuf_class.DESCRIPTOR.fields_by_name:
                raise ValueError(f"'{field_name}' field not found in protobuf message '{protobuf_class.DESCRIPTOR.name}'")

            # If it is a nested message or Oneof field
            field_message_type = protobuf_class.DESCRIPTOR.fields_by_name[field_name].message_type
            if field_message_type is not None:
                field_message_class = load_proto_class_from_protobuf_descriptor(field_message_type)
                # It's a nested message, go deeper
                if i + 1 < len(fields):
                    return ExperimentBuilder._recursive_search_(field_message_class, '.'.join(fields[i + 1:]))
                # It's a Oneof
                return field_message_class, None
            # It's a scalar or repeated field
            else:
                return protobuf_class, field_name

    def build(self, **kwargs):
        all_args = set([*self._model_args.default_args] + [*kwargs])
        used_args = set()
        xp = self._recursive_build_(Experiment, self._model_args.default_args, copy.deepcopy(kwargs), used_args, self._hyperparameters)
        unused_args = all_args - used_args
        if len(unused_args) > 0:
            raise Exception('Unused keyword argument: {}'.format(', '.join(unused_args)))
        unused_hyperparameters = [k for k, v in self._hyperparameters.items() if v is None]
        if len(unused_hyperparameters) > 0:
            raise Exception('hyperparameter not found: {}'.format(', '.join(unused_hyperparameters)))
        for k, v in self._hyperparameters.items():
            xp.hyperparameters[k].CopyFrom(v)
        return xp

    @staticmethod
    def _recursive_build_(protobuf_class, default_args, kwargs, used_args, hyperparameters):
        def convert_to_dict(value):
            """Convert a protobuf message into a dict"""
            if isinstance(value, Message):
                value = json_format.MessageToDict(value, including_default_value_fields=True, preserving_proto_field_name=True)
            elif isinstance(value, dict):
                pass  # nothing to do
            return value

        def check_valid_hp_value(field):
            """
            Check if given kwarg is in the hyperparameter distribution
            """
            # check that the field value is in the defined hyperparameter distribution range
            if field.name in hp_to_field_name:
                value = kwargs[field.name]
                # Check if it is a OneOf and take the only value
                if field.message_type is not None:
                    entries = kwargs[field.name].keys()
                    assert len(entries) == 1, f'{entries} should be of lenght one for field {field.name}'
                    value = list(entries)[0]
                hp = hyperparameters[hp_to_field_name[field.name]]
                distribution_type = hp.WhichOneof('distribution')
                if distribution_type == 'categorical':
                    values = [getattr(v, v.WhichOneof('value')) for v in hp.categorical.values]
                    assert value in values, f'{value} not in the given hyperparameter categorical distribution ({values})'
                else:
                    distribution = getattr(hp, distribution_type)
                    min = 1
                    max = -1
                    if distribution_type in ['uniform', 'log_uniform']:
                        min = distribution.min
                        max = distribution.max
                    elif distribution_type == 'normal':
                        min = distribution.mu - 5 * distribution.sigma
                        max = distribution.mu + 5 * distribution.sigma
                    assert min <= kwargs[field.name] <= max, f'{kwargs[field.name]} not in the given hyperparameter {distribution_type} distribution ({min}, {max})'

        real_args = {}

        unused_default_args = default_args.keys() - set([f.name for f in protobuf_class.DESCRIPTOR.fields])
        if len(unused_default_args) > 0:
            raise Exception('Unexpected default keyword argument: {}'.format(', '.join(unused_default_args)))

        hp_to_field_name = {k.split('.')[-1]: k for k in hyperparameters.keys()}

        # The oneof has fields which are also present in the protobuf fields.
        # We can hence identify the oneof fields which should be skipped, by removing the selected oneof field.
        # We identify the selected oneof field by its presence in the kwargs or default_args parameters, where kwargs has the higher priority
        skipped_fields = []
        for oneof in protobuf_class.DESCRIPTOR.oneofs:
            fields = [field.name for field in oneof.fields]
            # Identify selected one of fields
            selected = set(fields) & set(kwargs.keys()) if len(set(fields) & set(kwargs.keys())) > 0 else set(fields) & set(default_args.keys())
            # We cannot have more than 1 selected oneof field.
            assert len(selected) <= 1, "Two or more values are given for the one-of '{}' (error when processing '{}'): {}".format(oneof.name, protobuf_class.DESCRIPTOR.name, selected)
            # The skipped fields are the symmetric difference of the possible and selected oneof fields
            skipped_fields += list(set(fields) ^ selected)

        for field in protobuf_class.DESCRIPTOR.fields:
            # Skip fields which are unselected oneof fields
            if field.name in skipped_fields:
                continue

            # If the field is a scalar or a list ...
            if field.message_type is None or field.label == FieldDescriptor.LABEL_REPEATED:
                # ... there is only one possible value and kwargs has higher priority
                if field.name in kwargs:
                    check_valid_hp_value(field)
                    real_args[field.name] = convert_to_dict(kwargs.pop(field.name))
                elif field.name in default_args:
                    real_args[field.name] = default_args[field.name]

            else:
                # If the field is required, we build it
                # --> then we build the message
                args = {}
                used = False
                if field.name in kwargs:
                    check_valid_hp_value(field)
                    args = convert_to_dict(kwargs.pop(field.name))
                    used = True
                elif field.name in default_args:
                    args = default_args[field.name]
                    used = True
                # This fields is a protobuf message, we build it recursively
                field_message_class = load_proto_class_from_protobuf_descriptor(field.message_type)
                exp_builder = ExperimentBuilder._recursive_build_(field_message_class, args, kwargs, used_args, hyperparameters)
                if used or field.label == FieldDescriptor.LABEL_REQUIRED:
                    real_args[field.name] = exp_builder

        used_args.update([*real_args])
        return protobuf_class(**real_args)
