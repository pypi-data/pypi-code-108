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
"""Renderer of histogram plots for MPL."""
import functools

from sylib.report import editor_type
from sylib.report import plugins
mpl_backend = plugins.get_backend('mpl')


def create_layer(binding_context, parameters):
    """
    Build layer for MPL and bind properties using binding context.
    :param binding_context: Binding context.
    :param parameters: Dictionary containing:
                       'layer_model': a models.GraphLayer instance,
                       'axes': the MPL-axes to add layer to,
                       'canvas': canvas (Qt-widget) that we are rendering to,
                       'z_order': Z-order of layer.
    :return: MPL-element which can be added to Axes.
    """
    # This is our context to be shared by setters of bindings.
    context = {
        'binding_context': binding_context,
        'lines': [],
        'layer_model': parameters['layer_model'],
        'axes': parameters['axes'],
        'canvas': parameters['canvas'],
        'z_order': parameters['z_order'],
        'properties': []
    }

    def update_data(context_, _):
        # Remove old lines.
        for line in context_['lines']:
            line.remove()
        context_['lines'] = []

        (data_,), _ = context_['layer_model'].extract_data_and_properties()
        if len(data_) == 0:
            return
        properties_ = parameters['layer_model'].properties_as_dict()
        for x in data_:
            context_['lines'].append(context_['axes'].axvline(
                x, zorder=context_['z_order'],
                color=properties_['color'].get(),
                linewidth=properties_['line-width'].get(),
                alpha=properties_['alpha'].get()))

        context_['canvas'].draw_idle()

    # Bind values.
    _, (data_source_property,) = \
        context['layer_model'].extract_data_and_properties()

    # This is used to force update of axis range.
    data_source_property.editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)

    # Bind line properties.
    properties = parameters['layer_model'].properties_as_dict()

    for property_name in ('color', 'line-width', 'alpha'):
        mpl_backend.wrap_and_bind(binding_context,
                                  parameters['canvas'],
                                  properties[property_name],
                                  properties[property_name].get,
                                  functools.partial(update_data, context))
