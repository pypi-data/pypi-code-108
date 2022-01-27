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
import re
from collections.abc import Sequence

import numpy as np


SCALE_TYPES = (
    'linear',
    'log'
)


re_color = re.compile('#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})',
                      flags=re.IGNORECASE)


color_string_to_tuple = lambda color_string: tuple(
    [int(x, 16) for x in re_color.match(color_string).groups()])


interpolate_color_tuples = lambda color1_tuple, color2_tuple, weight: tuple(
    [int((c2 - c1) * weight + c1)
     for c1, c2 in zip(color1_tuple, color2_tuple)])


tuple_to_color_string = lambda color_tuple: '#{:02x}{:02x}{:02x}'.format(
    *color_tuple)


class IdentityScale(object):
    """Scale doing nothing but returning the same value it receives."""

    def f(self, x):
        return x

    def __call__(self, domain_value):
        if (isinstance(domain_value, (Sequence, np.ndarray)) and
                not isinstance(domain_value, str)):
            # This way we can return the same type of sequence as we get in.
            if domain_value.__class__ == np.ndarray:
                range_value = np.array([self.f(x) for x in domain_value])
            else:
                range_value = domain_value.__class__(
                    [self.f(x) for x in domain_value])
        else:
            range_value = self.f(domain_value)
        return range_value


class LinearScale(IdentityScale):
    """Linear interpolation scale."""

    def __init__(self, domain, range_, invalid_value=None):
        """Create a linear scale"""
        self._domain = domain
        self._range = range_
        self._invalid_value = invalid_value
        if isinstance(self._range[0], str):
            self.f = self.color_f
        else:
            self.f = self.numeric_f

    def color_f(self, x):
        # If set, return invalid color for NaN values.
        if self._invalid_value is not None and np.isnan(x):
            return self._invalid_value

        # Hold end values if outside domain.
        if x <= self._domain[0]:
            return self._range[0]
        elif x >= self._domain[-1]:
            return self._range[-1]

        # Find surrounding items.
        for i, (x1, x2) in enumerate(zip(self._domain[0:-1],
                                                   self._domain[1:])):
            if x1 <= x <= x2:
                color1 = color_string_to_tuple(self._range[i])
                color2 = color_string_to_tuple(self._range[i + 1])
                weight = float(x - x1) / float(x2 - x1)
                break

        mid_color = interpolate_color_tuples(color1, color2, weight)

        return tuple_to_color_string(mid_color)

    def numeric_f(self, x):
        # If set, return invalid color for NaN values.
        if self._invalid_value is not None and np.isnan(x):
            return self._invalid_value

        return np.interp(x, self._domain, self._range)

    def __call__(self, domain_value):
        if self.f == self.color_f:
            result = super(LinearScale, self).__call__(domain_value)
            return result
        # Optimization since np.interp handles everything.
        return self.f(domain_value)


class OrdinalScale(IdentityScale):
    """
    Ordinal scale with discrete items. No interpolation. Just lookup.
    If the domain value does not exist a ValueError is thrown.
    """

    def __init__(self, domain, range_):
        self._domain_to_range = dict(list(zip(domain, range_)))

    def f(self, x):
        # Just return the range value corresponding to the index
        # of the domain value.
        return self._domain_to_range[x]


def create_scale(scale_type, domain, range_):
    if scale_type == 'identity':
        return IdentityScale()
    elif scale_type == 'linear':
        return LinearScale(domain, range_)
    elif scale_type == 'ordinal':
        return OrdinalScale(domain, range_)
    return None


class ScaleBinding(object):
    data_id = None
    scale_id = None

    def __init__(self, data_id, scale_id):
        self.data_id = data_id
        self.scale_id = scale_id

    def as_dict(self):
        return {
            'data': self.data_id,
            'scale': self.scale_id
        }
