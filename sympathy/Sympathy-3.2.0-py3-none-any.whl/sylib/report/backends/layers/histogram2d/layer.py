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

from sylib.report import icons
from sylib.report import layers


class Layer(layers.Layer):
    """Heatmap layer."""

    meta = {
        'icon': icons.SvgIcon.histogram2d,
        'label': 'Heatmap',
        'default-data': {
            'type': 'histogram2d',
            'data': [
                {
                    'source': '',
                    'axis': ''
                },
                {
                    'source': '',
                    'axis': ''
                }
            ]
        }
    }
    property_definitions = collections.OrderedDict((
        ('name', {'type': 'string',
                  'label': 'Name',
                  'icon': icons.SvgIcon.blank,
                  'default': 'Heatmap Plot'}),

        ('x-bin-count', {'type': 'integer',
                         'label': 'X Bin Count',
                         'icon': icons.SvgIcon.blank,
                         'range': {'min': 1, 'max': 100000, 'step': 1},
                         'default': 10}),

        ('y-bin-count', {'type': 'integer',
                         'label': 'Y Bin Count',
                         'icon': icons.SvgIcon.blank,
                         'range': {'min': 1, 'max': 100000, 'step': 1},
                         'default': 10}),

        ('reduce-func', {'type': 'list',
                         'label': 'Reduction function',
                         'icon': icons.SvgIcon.blank,
                         'options': ['count', 'median', 'mean', 'min', 'max'],
                         'default': 'count'}),

        ('z-source', {'type': 'datasource',
                      'label': 'Bin values',
                      'icon': icons.SvgIcon.blank,
                      'default': ''}),

        ('color', {'type': 'colorscale',
                   'label': 'Color Scale',
                   'icon': icons.SvgIcon.blank,
                   'default': 'pink'}),

        ('colorbar', {'type': 'boolean',
                      'label': 'Colorbar',
                      'icon': icons.SvgIcon.blank,
                      'default': True}),

        ('draw-numbers', {'type': 'boolean',
                          'label': 'Draw numbers',
                          'icon': icons.SvgIcon.blank,
                          'default': False}),

        ('draw_edges', {'type': 'boolean',
                        'label': 'Draw edges',
                        'icon': icons.SvgIcon.blank,
                        'default': False}),

        ('edgecolor', {'type': 'color',
                       'label': 'Edge color',
                       'icon': icons.SvgIcon.blank,
                       'default': '#000000'}),

        ('smoothing', {'type': 'list',
                       'label': 'Smoothing',
                       'icon': icons.SvgIcon.blank,
                       'options': ['nearest', 'bilinear', 'bicubic'],
                       'default': 'nearest'}),

        ('alpha', {'type': 'float',
                   'label': 'Alpha',
                   'range': {'min': 0.0, 'max': 1.0, 'step': 0.1},
                   'icon': icons.SvgIcon.blank,
                   'default': 1.0})
    ))
