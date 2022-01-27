# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

import collections

from . import editor_type
from . import scales


type_to_editor = {
    'boolean': editor_type.Boolean,
    'list': editor_type.ImmutableList,
    'float': editor_type.Float,
    'integer': editor_type.Integer,
    'color': editor_type.Color,
    'colorscale': editor_type.ColorScale,
    'string': editor_type.String,
    'datasource': editor_type.DataSource,
    'image': editor_type.Image
}


class Layer(object):
    """
    A layer contains a dictionary with definitions of all available properties.
    If a property is missing in one layer it must be added to the data
    structure containing its default value.
    """

    property_definitions = None
    properties = None

    @classmethod
    def create_properties(cls, layer_model, property_class):
        """
        Create layer properties.
        :param layer_model: models.GraphLayer object.
        :param property_class: Usually models.Property.
        """
        properties = collections.OrderedDict()

        # Handle specified and unspecified properties.
        for k, v in list(cls.property_definitions.items()):
            # If we have already added the property, skip it.
            if k in properties:
                continue
            # Add missing parameter into model containing default value.
            if 'options' in v:
                def create_options_getter(x):
                    return lambda: x['options']
                options_getter = create_options_getter(v)
            else:
                options_getter = lambda: None
            editor = type_to_editor[v['type']](options_getter)
            editor.value_range = v.get('range', None)
            is_bindable = v.get('scale_bindable', False)
            parameters = {
                'property': k,
                'label': v['label'],  # Label of property.
                'icon': v['icon'],    # Icon of property.
                'editor': editor,
                'data': layer_model.data,
                'scale_bindable': is_bindable
            }
            # Side-effects...
            # Add specified property to data dict.
            if k in layer_model.data:
                if (is_bindable and
                   isinstance(layer_model.data[k], collections.Mapping) and
                   'binding' in layer_model.data[k]):
                    if layer_model.data[k]['binding'] is not None:
                        parameters['scale_binding'] = scales.ScaleBinding(
                            layer_model.data[k]['binding']['data'],
                            layer_model.data[k]['binding']['scale'])
                elif (not is_bindable and
                      isinstance(layer_model.data[k], collections.Mapping) and
                      'binding' in layer_model.data[k]):
                    # Correct structure if binding is not allowed but
                    # data provides it anyway.
                    layer_model.data[k] = layer_model.data[k]['value']
            # Add default property to data dict.
            else:
                if is_bindable:
                    layer_model.data[k] = {
                        'value': v['default'],
                        'binding': None
                    }
                else:
                    layer_model.data[k] = v['default']
            properties[k] = property_class(parameters, parent=layer_model)
            # Make sure that proper updates happen when a layer is renamed.
            if k == 'name':
                properties[k].editor.tags.add(
                    editor_type.EditorTags.force_update_after_edit)

        return properties
