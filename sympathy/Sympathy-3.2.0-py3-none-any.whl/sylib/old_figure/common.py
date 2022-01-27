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

from . import colors
from sylib.util import base_eval


REPLACE_AXIS_TYPE = {'x': 'bottom',
                     'x1': 'bottom',
                     'x2': 'top',
                     'y': 'left',
                     'y1': 'left',
                     'y2': 'right'}


def parsing_context(data_table):
    context = {'table': data_table, 'arg': data_table}
    return context


def parse_value(text, data_table, extra_vars=None):
    """
    Evaluate expression in a limited python environment.

    If evaluation fails, the input text will be returned as
    ``unicode``.

    Parameters
    ----------
    text : unicode or str
    data_table : sympathy.api.table.File
    extra_vars : dict, optional

    Returns
    -------
    Returns the evaluated text.
    """
    context = parsing_context(data_table)
    if extra_vars:
        context.update(extra_vars)
    try:
        parsed_value = base_eval(str(text), context)
    except (NameError, SyntaxError):
        parsed_value = str(text)
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
    else:
        return t(value)
