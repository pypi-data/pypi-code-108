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

import numpy as np

from sylib.report import layers
from sylib.report import icons


class Layer(layers.Layer):
    """Bar layer."""

    meta = {
        'icon': icons.SvgIcon.bar,
        'label': 'Bar Plot',
        'default-data': {
            'type': 'bar',
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
                  'default': 'Bar Plot'}),

        ('bar-width', {'type': 'float',
                       'label': 'Bar Width',
                       'icon': icons.SvgIcon.blank,
                       'range': {'min': 0, 'max': np.inf, 'step': 0.5},
                       'default': 0.5}),

        ('x-offset', {'type': 'float',
                      'label': 'Horizontal Offset',
                      'icon': icons.SvgIcon.blank,
                      'range': {'min': -np.inf, 'max': np.inf, 'step': 0.5},
                      'default': 0.0}),

        ('face-color', {'type': 'color',
                        'label': 'Face Color',
                        'icon': icons.SvgIcon.blank,
                        'default': '#809dd5'}),

        ('edge-color', {'type': 'color',
                        'label': 'Edge Color',
                        'icon': icons.SvgIcon.blank,
                        'default': '#000000'}),

        ('alpha', {'type': 'float',
                   'label': 'Alpha',
                   'range': {'min': 0.0, 'max': 1.0, 'step': 0.1},
                   'icon': icons.SvgIcon.blank,
                   'default': 1.0})
    ))
