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

from sylib.report import icons
from sylib.report import layers


class Layer(layers.Layer):
    """Vertical line layer."""

    meta = {
        'icon': icons.SvgIcon.vlines,
        'label': 'Vertical lines',
        'default-data': {
            'type': 'vline',
            'data': [
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
                  'default': 'Vertical Line'}),

        ('line-width', {'type': 'float',
                        'label': 'Line Width',
                        'icon': icons.SvgIcon.blank,
                        'range': {'min': 0, 'max': np.inf, 'step': 0.1},
                        'default': 1.0}),

        ('color', {'type': 'color',
                   'label': 'Color',
                   'icon': icons.SvgIcon.blank,
                   'default': '#000000'}),

        ('alpha', {'type': 'float',
                   'label': 'Alpha',
                   'range': {'min': 0.0, 'max': 1.0, 'step': 0.1},
                   'icon': icons.SvgIcon.blank,
                   'default': 1.0})
    ))
