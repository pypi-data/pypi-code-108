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
import re
import itertools
import collections

import numpy as np
from matplotlib import colors as mpl_colors
from sympathy.platform.exceptions import sywarn


def get_known_mpl_colors(add_single_letter_colors=True):
    colors = list(mpl_colors.cnames.items())
    # Add the single letter colors.
    if add_single_letter_colors:
        for name, rgb in mpl_colors.ColorConverter.colors.items():
            hex_ = mpl_colors.rgb2hex(rgb)
            colors.append((name, hex_.lower()))
    # sort by name
    colors.sort()
    return dict(colors)


SEQUENTIAL_COLORMAPS = collections.OrderedDict([
    ('viridis', 'viridis'),
    ('magma', 'magma'),
    ('inferno', 'inferno'),
    ('plasma', 'plasma'),
    ('gray', 'gray')])
DIVERGING_COLORMAPS = collections.OrderedDict([
    ('brown - blue/green (diverging)', 'BrBG'),
    ('red - blue (diverging)', 'RdBu'),
    ('spectral (diverging)', 'Spectral')])
QUALITATIVE_COLORMAPS = collections.OrderedDict([
    ('accent (qualitative 8)', 'Accent'),
    ('pastel1 (qualitative 9)', 'Pastel1'),
    ('tab10  (qualitative 10)', 'tab10'),
    ('tab20  (qualitative 20)', 'tab20'),
    ('tab20b (qualitative 20)', 'tab20b'),
    ('tab20c (qualitative 20)', 'tab20c')])
COLORMAPS = collections.OrderedDict(itertools.chain(
    [('auto', None)], SEQUENTIAL_COLORMAPS.items(),
    DIVERGING_COLORMAPS.items(),
    QUALITATIVE_COLORMAPS.items()))
COLORS = get_known_mpl_colors()
COLORS_INV = {v.lower(): k for k, v in
              get_known_mpl_colors(add_single_letter_colors=False).items()}

COLOR_CYCLES = collections.OrderedDict([
    ('default', ['1f77b4', 'ff7f0e', '2ca02c', 'd62728', '9467bd',
                 '8c564b', 'e377c2', '7f7f7f', 'bcbd22', '17becf']),
    ('dark-bright', ['1f77b4', 'aec7e8', 'ff7f0e', 'ffbb78', '2ca02c',
                     '98df8a', 'd62728', 'ff9896', '9467bd', 'c5b0d5',
                     '8c564b', 'c49c94', 'e377c2', 'f7b6d2', '7f7f7f',
                     'c7c7c7', 'bcbd22', 'dbdb8d', '17becf', '9edae5']),
    ('four-shades', ['393b79', '5254a3', '6b6ecf', '9c9ede', '637939',
                     '8ca252', 'b5cf6b', 'cedb9c', '8c6d31', 'bd9e39',
                     'e7ba52', 'e7cb94', '843c39', 'ad494a', 'd6616b',
                     'e7969c', '7b4173', 'a55194', 'ce6dbd', 'de9ed6']),
    ('four-shades2', ['3182bd', '6baed6', '9ecae1', 'c6dbef', 'e6550d',
                      'fd8d3c', 'fdae6b', 'fdd0a2', '31a354', '74c476',
                      'a1d99b', 'c7e9c0', '756bb1', '9e9ac8', 'bcbddc',
                      'dadaeb', '636363', '969696', 'bdbdbd', 'd9d9d9']),
])


def get_vmin_vmax(name):
    if name in COLORMAPS.keys():
        name = COLORMAPS[name]
    if name in SEQUENTIAL_COLORMAPS.values():
        return (0, 1)
    if name in DIVERGING_COLORMAPS.values():
        return (0, 1)
    if name in QUALITATIVE_COLORMAPS.values():
        dct = {'Accent': 8, 'Pastel1': 9, 'tab10': 10,
               'tab20': 20, 'tab20b': 20, 'tab20c': 20}
        return (0, dct[name])
    sywarn("Invalid colormap name {}".format(name))
    return (0, 1)


def color2hex(color):
    """
    Convert any supported color to hex representation.

    An existing alpha channel will be lost.

    Parameters
    ----------
    color : str or unicode or list or tuple

    Returns
    -------
    unicode
    """
    color_rgb = mpl_colors.colorConverter.to_rgb(color)
    return mpl_colors.rgb2hex(color_rgb)


def parse_to_mpl_color(text):
    """
    Parse a color string to a valid matplotlib color tuple.

    `text` can be any valid mpl color string can be used
    (e.g. 'r', 'red', 'b', 'blue', etc.), a valid hex color,
     hex color with additional alpha channel or a string
     of 3-4 integers/floats which can be parsed by
     ast.literal_eval to a tuple of numbers.

    Parameters
    ----------
    text : str or unicode
        A string for the color.
        Examples:
            (0, 0, 0)
            (255, 255, 255, 255)
            (0.5, 0.5, 0.5)
            (1., 1., 1., 1.)
            #ffffff
            #fefefefe
            'r'
            'red'

    Returns
    -------
    color : list
        A list of four floats in the interval [0., 1.].
    """
    text = str(text)
    # hex color
    is_hex = re.search(r'#[0-9a-fA-F]{6,8}', text)
    is_float, is_int = parse_number_colors(text)

    if text in COLORS.keys():
        # named color
        return text
    elif is_hex:
        hex_c = is_hex.group() if is_hex is not None else None
        rgba = list(mpl_colors.hex2color(hex_c[:7]))
        if len(hex_c) == 9:
            rgba.append(int(hex_c[-2:], 16) / 255.)
        return rgba
    elif is_int is not None:
        return list(is_int / 255.)
    elif is_float is not None:
        return list(is_float)
    return None


def get_color_dev(text):
    """
    Returns the type used to define the color ('name', 'rgb', etc).

    Parameters
    ----------
    text : unicode
        The color defined as unicode.

    Returns
    -------
    str
        One of ['name', 'hex', 'rgb', 'rgba', 'rgbF', 'rgbaF', None].
    """
    text = str(text)
    is_float, is_int = parse_number_colors(text)

    if text in COLORS.keys():
        # named color
        return 'name'
    elif re.search(r'#[0-9a-fA-F]{6,8}', text):
        return 'hex'
    elif is_float is not None and len(is_float) == 3:
        return 'rgbF'
    elif is_float is not None and len(is_float) == 4:
        return 'rgbaF'
    elif is_int is not None and len(is_int) == 3:
        return 'rgb'
    elif is_int is not None and len(is_int) == 4:
        return 'rgba'
    return None


def parse_number_colors(text):
    """
    Check if a string contains 3 or 4 floats/ints representing a rgb(a) color.

    Parameters
    ----------
    text : unicode

    Returns
    -------
    is_float : np.ndarray or None
    is_int : np.ndarray or None
    """
    text = str(text)
    # rgb colors
    ex = r"(?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )"
    rx = re.compile(ex, re.VERBOSE)
    numbers = rx.findall(text)
    is_float = np.float_(numbers)
    if (is_float is None or np.any(is_float > 1.) or
            len(is_float) not in [3, 4]):
        is_float = None
    try:
        is_int = np.int_(numbers)
        if (is_int is None or np.any(is_int > 255) or
                len(is_int) not in [3, 4] or '.' in text):
            is_int = None
    except ValueError:
        is_int = None
    return is_float, is_int


def get_color_as_rgba_f(color):
    color_dev = get_color_dev(color)
    a = 1.
    if color_dev == 'name':
        hex_color = COLORS[color]
        rgbf = mpl_colors.hex2color(hex_color)
    elif color_dev == 'hex':
        rgbf = mpl_colors.hex2color(color[:7])
        if len(color) > 7:
            a = int(color[-2:], 16) / 255.
    elif color_dev == 'rgb':
        rgbf = parse_to_mpl_color(color)
    elif color_dev == 'rgba':
        rgbaf = parse_to_mpl_color(color)
        a = rgbaf[-1]
        rgbf = rgbaf[:3]
    elif color_dev == 'rgbF':
        rgbf = parse_to_mpl_color(color)
    elif color_dev == 'rgbaF':
        rgbaf = parse_to_mpl_color(color)
        rgbf = rgbaf[:3]
        a = rgbaf[-1]
    else:
        return None

    rgbaf = tuple(list(rgbf) + [a])
    return rgbaf
