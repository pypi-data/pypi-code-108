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
import numpy as np

from sylib.report import editor_type
from sylib.report import plugins
mpl_backend = plugins.get_backend('mpl')


def create_layer(binding_context, parameters):
    """
    Build layer for MPL and bind properties using binding context.

    Parameters
    ----------
    binding_context
        Binding context.
    parameters : dictionary
        Should contain:
            'layer_model': a models.GraphLayer instance,
            'axes': the MPL-axes to add layer to,
            'canvas': current canvas (QtWidget) we are rendering to,
            'z_order': Z-order of layer.

    Returns
    -------
    matplotlib.artist.Artist
        MPL-element which can be added to Axes.
    """
    # Find data for each axis.
    (x_data, y_data), data_source_properties = \
        parameters['layer_model'].extract_data_and_properties()

    properties = parameters['layer_model'].properties_as_dict()

    # Side-effect: Line2D-object added to axes.
    if len(x_data) == len(y_data) and len(x_data) > 0:
        if properties['restart'].get():
            line_objects = []
            decrease_mask = np.flatnonzero(np.diff(x_data) < 0)
            prev_i = 0
            for i in decrease_mask + 1:
                line_objects.extend(parameters['axes'].plot(
                    x_data[prev_i:i], y_data[prev_i:i],
                    zorder=parameters['z_order']))
                prev_i = i
            line_objects.extend(parameters['axes'].plot(
                x_data[prev_i:], y_data[prev_i:],
                zorder=parameters['z_order']))
        else:
            line_objects = parameters['axes'].plot(
                x_data, y_data, zorder=parameters['z_order'])
    else:
        line_objects = parameters['axes'].plot(
            0, 0, zorder=parameters['z_order'])

    _, data_source_properties = \
        parameters['layer_model'].extract_data_and_properties()

    # This is used to force update of axis range.
    data_source_properties[0].editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)
    data_source_properties[1].editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)
    properties['restart'].editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)

    # Bind stuff.
    for line_object in line_objects:
        mpl_backend.bind_artist(binding_context,
                                {'property': properties['line-style'],
                                 'getter': line_object.get_linestyle,
                                 'setter': line_object.set_linestyle,
                                 'canvas': parameters['canvas'],
                                 'kind': 'string'})

        mpl_backend.bind_artist(binding_context,
                                {'property': properties['line-width'],
                                 'getter': line_object.get_linewidth,
                                 'setter': line_object.set_linewidth,
                                 'canvas': parameters['canvas'],
                                 'kind': 'numeric'})

        mpl_backend.bind_artist(binding_context,
                                {'property': properties['line-color'],
                                 'getter': line_object.get_color,
                                 'setter': line_object.set_color,
                                 'canvas': parameters['canvas'],
                                 'kind': 'color'})

        mpl_backend.bind_artist(binding_context,
                                {'property': properties['alpha'],
                                 'getter': line_object.get_alpha,
                                 'setter': line_object.set_alpha,
                                 'canvas': parameters['canvas'],
                                 'kind': 'numeric'})
