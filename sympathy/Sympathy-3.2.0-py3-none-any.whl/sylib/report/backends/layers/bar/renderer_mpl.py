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
"""Renderer of bar plots for MPL."""
import functools
from sylib.report import editor_type
from sylib.report import plugins
backend = plugins.get_backend('mpl') # noqa

import numpy as np


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
    (x_data, y_data), data_source_properties = \
        parameters['layer_model'].extract_data_and_properties()

    # Side-effect: Rectangles and BarContainer added to axes.
    if len(x_data) == len(y_data) and len(x_data) > 0:
        patches = parameters['axes'].bar(x_data, y_data,
                                         zorder=parameters['z_order'])
    else:
        patches = parameters['axes'].bar(np.array([0]),
                                         np.array([0]),
                                         zorder=parameters['z_order'])

    # Bind data to patches.
    def update_x_values(canvas_, patch_list, layer_model_, _):
        properties_ = layer_model_.properties_as_dict()
        offset = properties_['x-offset'].get()
        try:
            (x_data_, y_data_), _ = \
                parameters['layer_model'].extract_data_and_properties()
            if len(x_data_) == len(y_data_) and len(x_data_) > 0:
                for rect, x_ in zip(patch_list, x_data_):
                    xy = rect.get_xy()
                    rect.set_xy((x_ + offset, xy[1]))
        except KeyError:
            pass
        canvas_.draw_idle()

    def update_x_offset(parameters_, value):
        try:
            (x_data_, y_data_), _ = \
                parameters['layer_model'].extract_data_and_properties()
            if len(x_data_) == len(y_data_) and len(x_data_) > 0:
                for rect, x_ in zip(parameters_['artists'](),
                                               x_data_):
                    xy = rect.get_xy()
                    rect.set_xy((x_ + value, xy[1]))
        except KeyError:
            pass
        parameters_['canvas'].draw_idle()

    def update_y_values(canvas_, patch_list, _):
        try:
            (x_data_, y_data_), _ = \
                parameters['layer_model'].extract_data_and_properties()
            if len(x_data_) == len(y_data_) and len(x_data_) > 0:
                for rect, y_ in zip(patch_list, y_data_):
                    xy = rect.get_xy()
                    # When y is negative we must use the negative "height" as
                    # base value and use a positive height to reach zero.
                    if y_ < 0:
                        rect.set_xy((xy[0], y_))
                    else:
                        rect.set_xy((xy[0], 0))
                    rect.set_height(abs(y_))
        except KeyError:
            pass
        canvas_.draw_idle()

    # Bind x- and y-values.
    backend.wrap_and_bind(
        binding_context,
        parameters['canvas'],
        source_property=data_source_properties[0],
        target_getter=data_source_properties[0].get,
        target_setter=functools.partial(update_x_values,
                                        parameters['canvas'], patches,
                                        parameters['layer_model']))
    # We want to force a total rebuild of the plot when the data source
    # changes to allow the layer to recreate the patches from scratch as is
    # done first in this function.
    data_source_properties[0].editor.tags.add(editor_type.EditorTags.
                                              force_rebuild_after_edit)

    backend.wrap_and_bind(
        binding_context,
        parameters['canvas'],
        source_property=data_source_properties[1],
        target_getter=data_source_properties[1].get,
        target_setter=functools.partial(update_y_values,
                                        parameters['canvas'], patches))
    # Same here, but for y-axis.
    data_source_properties[1].editor.tags.add(editor_type.EditorTags.
                                              force_rebuild_after_edit)

    # Bind patch properties.
    properties = parameters['layer_model'].properties_as_dict()

    backend.wrap_and_bind(
        binding_context,
        parameters['canvas'],
        source_property=properties['x-offset'],
        target_getter=properties['x-offset'].get,
        target_setter=functools.partial(
            update_x_offset,
            {'property': properties['x-offset'],
             'artists': lambda: patches,
             'data_source_func': data_source_properties[0].get,
             'canvas': parameters['canvas']}))

    backend.bind_artist_list(binding_context,
                             {'property': properties['bar-width'],
                              'artists': lambda: patches,
                              'getter_func': lambda obj:
                              obj.get_width,
                              'setter_func': lambda obj:
                              obj.set_width,
                              'canvas': parameters['canvas'],
                              'kind': 'numeric'})

    backend.bind_artist_list(binding_context,
                             {'property': properties['face-color'],
                              'artists': lambda: patches,
                              'getter_func': lambda obj:
                              obj.get_facecolor,
                              'setter_func': lambda obj:
                              obj.set_facecolor,
                              'canvas': parameters['canvas'],
                              'kind': 'color'})

    backend.bind_artist_list(binding_context,
                             {'property': properties['edge-color'],
                              'artists': lambda: patches,
                              'getter_func': lambda obj:
                              obj.get_edgecolor,
                              'setter_func': lambda obj:
                              obj.set_edgecolor,
                              'canvas': parameters['canvas'],
                              'kind': 'color'})

    backend.bind_artist_list(binding_context,
                             {'property': properties['alpha'],
                              'artists': lambda: patches,
                              'getter_func': lambda obj:
                              obj.get_alpha,
                              'setter_func': lambda obj:
                              obj.set_alpha,
                              'canvas': parameters['canvas'],
                              'kind': 'numeric'})
