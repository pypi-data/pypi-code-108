from abc import ABC, abstractmethod


class SectionInterface(ABC):

    @abstractmethod
    def append(self, control):
        pass

    @abstractmethod
    def json(self):
        pass

    @property
    @abstractmethod
    def controls(self):
        pass

    @property
    @abstractmethod
    def value_to_tag_map(self):
        pass


class Section(SectionInterface):
    """
    A list of `Control`s with a title on top.
    """

    def __init__(self, name):
        """
        Create an empty section

        Args:
            name (str): the section title.
        """
        self._name = name
        self._controls = []

    def append(self, control):
        """
        Appends a control. Return self to allow chaining append.
        """
        self._controls.append(control)
        return self

    def json(self):
        """
        Return the JSON representation of a section
        """
        return {
            'name': self._name,
            'controls': [ss.json() for ss in self._controls]
        }

    @property
    def controls(self):
        """
        Return the controls
        """
        return self._controls

    @property
    def value_to_tag_map(self):
        """
        Return the value_to_tag_map for this section. This is a dict
        with one entry per control that declares tags. The keys are
        the control property names, the values are a dict representing
        a mapping from the possible values to the tag values.

        For example, if a section has a select control named 'model'
        that declares a tag named 'backend' and a toggle named 'balance'
        the returned value will be:

        {
            "model": {
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
            "balance": {
                False: {}  // no value because the tag `balance` will be declared by default with
                True: {}   // appropriate value True or False.
            }
        }
        """
        result = {}
        for s in self._controls:
            if s.value_to_tag_map is not None:
                result[s.property_name] = s.value_to_tag_map
        return result


###############################################################################

class SectionGroup:
    """
    Use this class to regroup all the sections of the training form and generate JSON.
    """

    def __init__(self):
        """
        Builds a form for some given enabled `models` and with a given `default_model`.

        Args:
            models (list): a list of model keys like 'image_classification.pretraining_natural_rgb.sigmoid.efficientnet_b0'
            default_model (str): a default model key like 'image_classification.pretraining_natural_rgb.sigmoid.efficientnet_b0'
        """
        self._sections = []
        self._properties = set()

    def append(self, section):
        """
        Add a section to the form.

        Args:
            section (Section): an instance of Section

        Return:
            self: for chaining
        """
        for control in section.controls:
            if control.property_name in self._properties:
                raise Exception('Property already exists: {}'.format(control.property_name))
            self._properties.add(control.property_name)
        self._sections.append(section)
        return self

    @property
    def sections(self):
        return self._sections

    @property
    def controls(self):
        for section in self._sections:
            for control in section.controls:
                yield control
