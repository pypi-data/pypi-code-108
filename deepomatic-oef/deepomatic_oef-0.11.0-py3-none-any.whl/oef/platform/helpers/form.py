import copy
import json

from deepomatic.oef.configs.model_list import model_list
from deepomatic.oef.utils.experiment_builder import ExperimentBuilder

from .common import BACKEND_FILE
from .controls import ModelControl, SelectOption, SelectControl, ToggleControl
from .section import SectionGroup
from .tags import Tags, Backend


###############################################################################

class Form(SectionGroup):
    """
    Use this class to regroup all the sections of the training form and generate JSON.
    """

    def __init__(self, form_parameters):
        """
        Args:
            form_parameters (dict): dict from ViewType to 3-tuple (model_prefix, [model_key], default_model)
        """
        super(Form, self).__init__()
        self._enabled_models = {}
        self._default_models = {}
        for view_type, (model_prefix, enabled_models, default_model) in form_parameters.items():
            self._enabled_models[view_type] = [model_prefix + m for m in enabled_models]
            self._default_models[view_type] = model_prefix + default_model
            assert self._default_models[view_type] in self._enabled_models[view_type], 'Could not find default model: {} in [{}]'.format(self._default_models[view_type], self._enabled_models[view_type])

        self._model_control = None

    def append(self, section):
        super(Form, self).append(section)
        for control in section.controls:
            if isinstance(control, ModelControl):
                if self._model_control is not None:
                    raise Exception('There can be only one ModelControl in the form')
                self._model_control = control

    def json(self):
        """
        Return JSON describing the form to display in Vesta's front-end.
        See README.md for a description of the format.

        Return:
            The JSON that fully describe the training form in Vesta
        """
        json_payload = {
            'view_types': {},
        }

        # Load the backend map
        with open(BACKEND_FILE, 'r') as f:
            backends = json.load(f)
            backends = {k: Backend(v) for k, v in backends.items()}

        value_to_tag_map = {}
        for control in self.controls:
            if isinstance(control, ModelControl):
                continue  # this control is not configured yet
            if control.value_to_tag_map is not None:
                assert control.property_name not in value_to_tag_map
                value_to_tag_map[control.property_name] = control.value_to_tag_map

        # Generate the value_to_tag_map for all models
        model_property_name = self._model_control.property_name
        assert model_property_name not in value_to_tag_map
        value_to_tag_map[model_property_name] = {}
        for view_type in self._enabled_models:
            # Compute model select values and tags
            model_select_values = []
            model_select_tags = {}
            for model_key in self._enabled_models[view_type]:
                model_select_values.append(
                    SelectOption(
                        model_key,
                        model_list[model_key].display_name
                    )
                )
                model_select_tags[model_key] = Tags([backends[model_key]])
            # Set available models
            self._model_control.set_values_and_tags(model_select_values, model_select_tags)

            # Generate value_to_tag_map for models
            value_to_tag_map[model_property_name].update(self._model_control.value_to_tag_map)

            json_payload['view_types'][view_type.value] = {
                'model_property_name': self._model_control.property_name,
                'default_model': self._default_models[view_type],
                'sections': [section.json() for section in self._sections],
                'default_values': {
                    model_key: self._model_json_(model_key, backends) for model_key in self._enabled_models[view_type]
                }
            }

        json_payload['value_to_tag_map'] = value_to_tag_map
        # Some dictionary keys may be booleans (which is not JSON compatible):
        # by dumping and reloading to json, we ensure a json compatible format.
        # Booleans are converted to 'false' or 'true' when used in dict keys.
        return json.loads(json.dumps(json_payload))

    def _model_json_(self, model_key, backends):
        """
        A helper function to build the JSON that describes the default values of a given `model_key`.

        Args:
            model_key (str): a default model key like 'image_classification.pretraining_natural_rgb.sigmoid.efficientnet_b0'
            backends: A dict from model key to the corresponding backend

        Return:
            The JSON that fully describe the default values for this model.
        """
        builder = ExperimentBuilder(model_key)
        xp = builder.build()

        default_values = {}
        for control in self.controls:
            backend = backends[model_key]
            value = control.default_value(model_key, xp, backend)
            if value is None:
                continue
            default_values[control.property_name] = value
        return default_values

    def parse(self, payload, value_to_tag_map):
        """
        Convert a API POST request into an experiment protobuf
        """
        payload = copy.deepcopy(payload)

        # Set enabled tags
        tags = {}
        for control in self.controls:
            value = payload[control.property_name]
            self._update_enabled_tags_(value_to_tag_map, tags, control, value)
            if isinstance(control, (SelectControl, ToggleControl)):
                tags[control.property_name] = value

        # Build protobuf
        model_key = payload.pop(self._model_control.property_name)
        experiment = ExperimentBuilder(model_key).build()

        for control in self.controls:
            if isinstance(control, ModelControl):
                continue  # This is the model select, we already used its value
            value = payload.pop(control.property_name)
            if control.is_visible(tags):
                control.protobuf_setter_fn(experiment, value)

        return experiment

    def _update_enabled_tags_(self, value_to_tag_map, tags, control, value):
        if control.property_name in value_to_tag_map:
            if isinstance(value, bool):
                # Boolean value will be silently dumped as "true" and "false" in the
                # JSON default_models.json.
                tags.update(value_to_tag_map[control.property_name][str(value).lower()])
            else:
                tags.update(value_to_tag_map[control.property_name][value])
