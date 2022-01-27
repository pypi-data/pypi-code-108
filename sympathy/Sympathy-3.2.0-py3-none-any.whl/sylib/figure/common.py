# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
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
from matplotlib import colors as mpl_colors

from sylib.figure import colors
from sylib.util import base_eval


REPLACE_AXIS_TYPE = {'x': 'bottom',
                     'x1': 'bottom',
                     'x2': 'top',
                     'y': 'left',
                     'y1': 'left',
                     'y2': 'right'}


def parse_value(value_text, data_table, extra_vars=None):
    """
    Evaluate expression in a limited python environment.

    Parameters
    ----------
    value_text : str
        The string that should be evaluated to produce the value.
    data_table : sympathy data type (e.g. sympathy.api.table.File)
        The input port that should be available during eval under the name arg.
    extra_vars : dict, optional
        Extra variables that will be available during eval.

    Returns
    -------
    Returns the evaluated text, or None if there was an error.
    """
    context = {'arg': data_table}
    if extra_vars:
        context.update(extra_vars)
    try:
        parsed_value = base_eval(str(value_text), context)
    except Exception:
        parsed_value = None
    return parsed_value


def verify_options(value, options):
    """Check if value is within the options."""
    if value in options:
        return value
    return None


def parse_type(value, t, options=None):
    if t == 'colortype':
        if (colors.get_color_dev(value) in ['rgb', 'rgba', 'rgbF', 'rgbaF'] or
                mpl_colors.is_color_like(value)):
            return value
        else:
            # TODO: add some validation for python expressions
            return value
    elif t == 'options':
        return verify_options(str(value), options)
    elif t == 'axesposition':
        if value in REPLACE_AXIS_TYPE.keys():
            value = REPLACE_AXIS_TYPE[value]
        return verify_options(value, options)
    elif t == bool:
        return value == 'True'
    else:
        return t(value)
