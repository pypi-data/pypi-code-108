from abc import ABC, abstractmethod
from enum import Enum
import functools
from google.protobuf.descriptor import FieldDescriptor

from deepomatic.oef.utils.class_helpers import load_proto_class_from_protobuf_descriptor
from deepomatic.oef.protos.experiment_pb2 import Experiment

from .common import CHECK_TYPE, CHECK_LIST, CHECK_DICT
from .section import SectionInterface
from .tags import Tags


###############################################################################

class ControlType(Enum):
    """
    Form control types
    """
    SELECT = 'select'
    INPUT = 'input'
    TOGGLE = 'toggle'


###############################################################################

class DisplayCondition:
    """
    Used to decide whether or not a control should be displayed.
    A DisplayCondition works by looking at the value of one tag.
    If this value is in a pre-determined set, then the condition
    is true. By combining multiple conditions in a list, one can
    define complex conditions.
    """

    def __init__(self, tag, allowed_values):
        """
        Create a DisplayCondition.

        Args:
            tag (str): The name of the tag to watch.
            allowed_values (list of str): If the tag takes one of this value then the condition
                is satisfied.
        """
        self._tag = CHECK_TYPE(tag, str)
        self._allowed_values = CHECK_TYPE(allowed_values, list, allow_none=True)

    def json(self):
        """
        Convert the object into a Python dict which is JSON-serializable.
        """
        return {
            'tag': self._tag,
            'allowed_values': self._allowed_values
        }

    def is_visible(self, tags):
        """
        Return true if control is visible

        Args:
            tags (dict): dict of tags (str) to their values (str)

        Return True if tag belongs to allowed values.
        """
        return tags[self._tag] in self._allowed_values


class DisplayGroup(SectionInterface):
    """
    Used to inject a display condition in multiple controls at once.

    Typical use:

    DisplayGroup(section, [condition1, condition2])
        .append(control1)
        .append(control2)
    """

    def __init__(self, parent, display_ifs):
        """
        Create a DisplayGroup given a parent and a display condition:
        all controls attached to the parent will receive the same visibility
        condition on top of them own visibility conditions.

        Args:
            parent (mixed): An instance of Section or DisplayGroup
            display_ifs (list of DisplayCondition): A list of DisplayCondition
        """
        assert hasattr(parent, 'append')
        self._parent = parent
        self._display_ifs = CHECK_LIST(display_ifs, DisplayCondition)

    def append(self, control):
        """
        Add a control to the DisplayGroup

        Args:
            control: an instance of Control
        """
        control.add_display_ifs(self._display_ifs)
        self._parent.append(control)
        return self

    def json(self):
        return self._parent.json()

    @property
    def controls(self):
        return self._parent.controls

    @property
    def value_to_tag_map(self):
        return self._parent.value_to_tag_map


###############################################################################

def protobuf_iterate(protobuf, key, check_last_one=True):
    keys = key.split('.')
    last_i = len(keys) - 1
    for i, key in enumerate(keys):
        if i < last_i or check_last_one:
            assert hasattr(protobuf, key), "Expecting finding the attribute '{}' but could not find one in protobuf message '{}'".format(key, protobuf.DESCRIPTOR.name)
        if i == last_i:
            return protobuf, key
        else:
            protobuf = getattr(protobuf, key)


def set_protobuf_value(protobuf, value, key):
    protobuf, last_key = protobuf_iterate(protobuf, key)
    setattr(protobuf, last_key, value)


def set_protobuf_oneof(protobuf, value, key):
    """The oneof name is assumed to be the last key"""
    protobuf, last_key = protobuf_iterate(protobuf, key, check_last_one=False)
    if protobuf.WhichOneof(last_key) != value:
        field = getattr(protobuf, value)
        field_descriptor = protobuf.DESCRIPTOR.fields_by_name[value]
        field_message_class = load_proto_class_from_protobuf_descriptor(field_descriptor.message_type)
        field.MergeFrom(field_message_class())


def check_protobuf_path(path, oneof=False):
    last_protobuf, oneof_name = protobuf_iterate(Experiment(), path, check_last_one=not oneof)
    if oneof:
        return last_protobuf.DESCRIPTOR.oneofs_by_name[oneof_name]
    else:
        return getattr(last_protobuf, oneof_name)


###############################################################################

class GetDefaultValueInterface(ABC):

    @abstractmethod
    def __call__(self, model_key, experiment, backend):
        """
        Return a default value for the specified model.

        Args:
            model_key: The model key as in model_list.py
            experiment: a Experiment protobuf
            backend: An instance of Backend tag

        Return:
            The default value.
        """


class GetProtobufValue(GetDefaultValueInterface):
    """
    A helper that represent a callable used to fetch the default value in the ModelArguments instance.
    """

    def __init__(self, value_key):
        """
        Args:
            value_key: A dot-separated path to the value of interest as stored in model.default_args.
                       For exemple: 'trainer.initial_learning_rate'
        """
        self._value_key = value_key

    def __call__(self, model_key, experiment, backend):
        """See GetDefaultValueInterface"""
        protobuf, last_key = protobuf_iterate(experiment, self._value_key)
        value = getattr(protobuf, last_key)
        field = protobuf.DESCRIPTOR.fields_by_name[last_key]
        if field.type == FieldDescriptor.TYPE_FLOAT:
            # Float protobuf fields will generate rounding error when converted back to double.
            # For example storing 0.9 in a float protobuf and reading it in Python would return
            # the 64 bits value 0.8999999761581421.
            # The hack below allow to display the value back with the proper number of decimals
            # to get a proper rounding and parse it in 64 bits to get back the initial value.
            value = float("{:f}".format(value))
        return value


class GetProtobufOneof(GetDefaultValueInterface):
    """
    A helper that represent a callable used to fetch the default oneof field in the ModelArguments instance.
    """

    def __init__(self, oneof_key):
        """
        Args:
            oneof_key: A dot-separated path to the value of interest as stored in model.default_args.
                       For exemple: 'trainer.initial_learning_rate'
        """
        self._oneof_key = oneof_key

    def __call__(self, model_key, experiment, backend):
        """See GetDefaultValueInterface"""
        protobuf, last_key = protobuf_iterate(experiment, self._oneof_key, check_last_one=False)
        return protobuf.WhichOneof(last_key)


class ConstantDefaultValue:
    """
    A helper that return a constant value when called
    """

    def __init__(self, default_value):
        """
        Args:
            default_value: The value to return
        """
        self._default_value = default_value

    def __call__(self, model_key, experiment, backend):
        """See GetDefaultValueInterface"""
        return self._default_value


###############################################################################

class Control:

    def __init__(self, property_name, protobuf_setter_fn, message, control_type, default_value, check_control_default_fn, display_ifs=None, header=None):
        """
        Create a Control.

        Args:
            property_name (str): name attribute of the control in the front-end. The value of interest will be stored
                           in the JSON payload posted to the training API under this key.
            protobuf_setter_fn (callable): a function to parse the form post request: will be called with two arguments: (xp_protobuf, value).
                                           This function is expected to modify the protobuf inplace.
            message (str): a message to display in the front-end. Corresponds to the label of the control.
            control_type (ControlType): an instance of ControlType
            default_value (mixed): the default value for this control. It is either:
                - a callable accepting two arguments `model_key` (a string) and `model` (a ModelArguments instance).
                  This callable must return the default value for the given model.
                - a string: `GetProtobufValue` will be used to fetch this value in the model. If the string is empty,
                            `GetProtobufValue` will be called with the `property_name`.
                - constant: `check_control_default_fn` will be used to check the constant type
            check_control_default_fn: A function without argument that will check the constant in default_value and return the real constant to use.
            display_ifs (list): A list of DisplayCondition
        Return:
            The Control object.
        """
        # Sanity checks
        self._message = CHECK_TYPE(message, str)
        self._property_name = CHECK_TYPE(property_name, str)
        if protobuf_setter_fn is not None:
            assert callable(protobuf_setter_fn)
        self._protobuf_setter_fn = protobuf_setter_fn
        self._control_type = CHECK_TYPE(control_type, ControlType)
        self._display_ifs = CHECK_LIST(display_ifs, DisplayCondition)
        self._tags = None
        self._value_to_tag_map = None
        self._control_parameters = None

        if default_value is None or callable(default_value):
            self._default_value_fn = default_value
        elif isinstance(default_value, str):
            # If the default value is a string, we wrap it into GetProtobufValue
            if default_value == '':  # if empty, we use self._property_name by default
                default_value = self._property_name
            self._default_value_fn = GetProtobufValue(default_value)
        else:
            self._default_value_fn = ConstantDefaultValue(check_control_default_fn())

    def json(self):
        """
        Convert the control into a Python dict which is JSON-serializable.
        """
        as_json = {
            'message': self._message,
            'type': self._control_type.value,
            'property': self._property_name,
            'display_if': [d.json() for d in self._display_ifs],
            'tags': self._tags,
            'control_parameters': self._control_parameters,
        }
        return as_json

    def default_value(self, model_key, model, backend):
        """
        Return the control default value for this model.

        Args:
            model_key: The model key as in model_list.py
            model: a ModelArguments instance
        """
        if self._default_value_fn is None:
            return None
        return self._default_value_fn(model_key, model, backend)

    @property
    def property_name(self):
        """Return the property name"""
        return self._property_name

    @property
    def protobuf_setter_fn(self):
        return self._protobuf_setter_fn

    @property
    def value_to_tag_map(self):
        """
        Return the value_to_tag_map for this control. This is a dict
        representing a mapping from the possible values to the tag values.

        For example, the control declares a tag named 'backend', the returned value will be:

        {
            "image_classification.pretraining_natural_rgb.sigmoid.efficientnet_b0": {
                "backend": "tensorflow"
            },
            ... // as many keys as SelectOption in the control
            "image_detection.pretraining_natural_rgb.yolo_v3.darknet_53": {
                "backend": "darkenet"
            }
            // an additional tag named `model` will be declared by default, its
            // value will be the value of the `model` property.
        }
        """
        return self._value_to_tag_map

    def add_display_ifs(self, display_ifs):
        """
        Args:
            display_ifs (list): A list of DisplayCondition
        """
        self._display_ifs += display_ifs

    def is_visible(self, tags):
        """
        Return true if control is visible

        Args:
            tags (dict): dict of tags (str) to their values (str)

        Return:
            visible: True if control is visible
        """
        visible = True
        for condition in self._display_ifs:
            visible = visible and condition.is_visible(tags)
        return visible


###############################################################################

class SelectControl(Control):
    """A helper class to define a SELECT."""

    def __init__(self, property_name, protobuf_path, message, values, tags=None, display_ifs=None, default_value=''):
        """
        Creates a SELECT. See Control for a description of other arguments.

        Args:
            property_name: see Control
            message: see Control
            default_value: see Control
            values (list): a list of SelectOption.
            tags (dict): a dict mapping values to instances of type Tags
        """
        def check_control_default_fn():
            # if the default value is a constant, it must be an index of one of the options
            CHECK_TYPE(default_value, int, exclude_types=bool)
            assert default_value < len(values)
            return values[default_value].value

        # Check that property_name points to a protobuf value
        if protobuf_path is not None:
            try:
                oneof = check_protobuf_path(protobuf_path, oneof=True)
            except AssertionError as e:
                raise Exception("Could not find protobuf oneof corresponding to '{}': please check its value. Error is: {}".format(protobuf_path, str(e)))
            possible_values = set([f.name for f in oneof.fields])
            defined_values = set([v.value for v in values])
            unknown_values = defined_values - possible_values
            if len(unknown_values) > 0:
                raise Exception('Unkown select value(s): {}'.format(', '.join(unknown_values)))

            protobuf_setter_fn = functools.partial(set_protobuf_oneof, key=protobuf_path)
        else:
            # only ModelControl can skip protobuf_setter_fn
            assert isinstance(self, ModelControl)
            protobuf_setter_fn = None

        if isinstance(default_value, str):
            # If the default value is a string, we wrap it into GetProtobufValue
            if default_value == '':  # if empty, we use protobuf_path by default
                assert protobuf_path is not None
                default_value = protobuf_path
            default_value = GetProtobufOneof(default_value)

        super(SelectControl, self).__init__(
            property_name,
            protobuf_setter_fn,
            message,
            ControlType.SELECT,
            default_value,
            check_control_default_fn,
            display_ifs
        )
        self._set_values_and_tags_(values, tags)

    def _set_values_and_tags_(self, values, tags=None):
        """
        Only used to set the model list.

        Args: see __init__
        """
        self._tags = [self._property_name]
        self._value_to_tag_map = None

        # Sanity check
        CHECK_LIST(values, SelectOption)
        if tags is not None:
            CHECK_DICT(tags, Tags)
            assert tags.keys() == set([v.value for v in values])
            additional_tags = None
            for t in tags.values():
                if additional_tags is None:
                    additional_tags = t.tags.keys()
                else:
                    assert additional_tags == t.tags.keys()
            self._tags += list(additional_tags)
            self._value_to_tag_map = {key: t.tags for key, t in tags.items()}
        else:
            self._value_to_tag_map = {v.value: {} for v in values}

        # Convert values into JSON
        self._control_parameters = {
            'values': [v.json() for v in values],
        }


class ModelControl(SelectControl):
    """A special control class for model selection."""

    def __init__(self, property_name, message):
        super(ModelControl, self).__init__(
            property_name,
            None,
            message,
            [],  # no values, they will be set thanks to set_values_and_tags
            # No default value for this one: the form sets its value at intialization
            default_value=None)

    def set_values_and_tags(self, values, tags=None):
        self._set_values_and_tags_(values, tags)


###############################################################################

class InputControl(Control):
    """A helper class to define an INPUT."""

    def __init__(self, property_name, message, min_value=None, max_value=None, increment_value=None, display_ifs=None, default_value=''):
        """
        A helper class to define a INPUT. See Control for a description of other arguments.

        Args:
            property_name: see Control
            message: see Control
            default_value: see Control
            min_value (number): the minimum value of the input.
            max_value (number): the maximum value of the input.
            increment_value (number): the increment value when click on the up and down arrows of the control.
        """
        def check_control_default_fn():
            CHECK_TYPE(default_value, (int, float), exclude_types=bool)
            return default_value

        # Check that property_name points to a protobuf value
        try:
            check_protobuf_path(property_name)
        except AssertionError as e:
            raise Exception("Could not find protobuf value corresponding to '{}': please check its value. Error is: {}".format(property_name, str(e)))

        super(InputControl, self).__init__(
            property_name,
            functools.partial(set_protobuf_value, key=property_name),
            message,
            ControlType.INPUT,
            default_value,
            check_control_default_fn,
            display_ifs
        )

        self._control_parameters = {}
        if min_value is not None:
            self._control_parameters['min_value'] = min_value
        if max_value is not None:
            self._control_parameters['max_value'] = max_value
        if increment_value is not None:
            self._control_parameters['increment_value'] = increment_value


###############################################################################

class ToggleControl(Control):
    """A helper class to define an TOGGLE."""

    def __init__(self, property_name, message, tags=None, display_ifs=None, default_value='', protobuf_setter_fn=None):
        """
        A helper class to define a TOGGLE. See Control for a description of other arguments.

        Args:
            property_name: see Control
            message: see Control
            default_value: see Control
            tags (tuple): if not None, must be a tuple of length 2 containing two dicts.
                The first (second) dict are the additional tags to set when the toggle is off (on), respectively.
                Each dict must have the same keys as additional_tags.
            additional_tags (list): A list of additional tags (so a list of str), i.e. that do not just refer to the property_name
        """
        def check_control_default_fn():
            CHECK_TYPE(default_value, bool)
            return default_value

        if protobuf_setter_fn is None:
            # Check that property_name points to a protobuf value
            try:
                check_protobuf_path(property_name)
            except AssertionError as e:
                raise Exception("Could not find protobuf value corresponding to '{}': please check its value or define `protobuf_setter_fn`. Error is: {}".format(property_name, str(e)))
            protobuf_setter_fn = functools.partial(set_protobuf_value, key=property_name)

        super(ToggleControl, self).__init__(
            property_name,
            protobuf_setter_fn,
            message,
            ControlType.TOGGLE,
            default_value,
            check_control_default_fn,
            display_ifs
        )

        # A toogle declares itself
        self._tags = [self._property_name]
        tags_off = {}
        tags_on = {}
        if tags is not None:
            # Sanity checks
            assert tags is not None
            CHECK_LIST(tags, Tags)
            assert len(tags) == 2
            tags_off, tags_on = tags
            tags_off = tags_off.tags
            tags_on = tags_on.tags
            assert tags_off.keys() == tags_on.keys()

            # Add additional tags to the list of tags
            self._tags += tags_on.keys()
        self._value_to_tag_map = {
            False: tags_off,
            True: tags_on
        }


###############################################################################

class SelectOption:
    """A helper class for controls of type SELECT to store the possible values"""

    def __init__(self, value, display_string, display_ifs=None):
        """
        Create a SelectOption instance.

        Args:
            value (str): the computer-friendly value for this option
            display_string (str): the human-friendly string to display
            display_ifs (list): A list of DisplayCondition

        Return:
            A SelectOption instance.
        """
        self._value = CHECK_TYPE(value, str)
        self._display_string = CHECK_TYPE(display_string, str)
        self._display_ifs = CHECK_LIST(display_ifs, DisplayCondition)

    def json(self):
        """
        Convert the object into a Python dict which is JSON-serializable.
        """
        return {
            'value': self._value,
            'display_string': self._display_string,
            'display_if': [d.json() for d in self._display_ifs]
        }

    @property
    def value(self):
        return self._value
