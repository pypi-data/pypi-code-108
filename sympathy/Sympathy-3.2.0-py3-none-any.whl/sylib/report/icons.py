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

import os.path
import Qt.QtGui as QtGui
from . import decorators

SIZE = 36
EMPTY_ICON = QtGui.QIcon()


class SvgIcon(object):
    blank = None
    data = 'data3.svg'
    chat = 'chat51.svg'
    graph = 'ascending7.svg'
    plot = 'graph.svg'
    coordinates = '3d76.svg'
    projection = 'textile.svg'
    plug = 'energy7.svg'
    x_axis = 'xaxis.svg'
    y_axis = 'yaxis.svg'
    z_axis = 'zaxis.svg'
    n_axis = 'naxis.svg'
    width = 'width3.svg'
    height = 'height6.svg'
    layers = 'layers.svg'
    layer = 'layer.svg'
    link = 'link5.svg'
    view = 'personal5.svg'
    ruler = 'ruler.svg'
    scales = 'scales2.svg'
    triangle = 'set1.svg'
    layout = 'layout.svg'
    text = 'label.svg'
    config = 'three115.svg'
    label = 'tag31.svg'
    list = 'list23.svg'
    pages = 'copy9.svg'
    page = 'page.svg'
    grid = 'squares8.svg'
    plus = 'add133.svg'
    minus = 'minus75.svg'
    picture = 'image.svg'
    # Icons for layers:
    scatter = 'scatter.svg'
    bar = 'barchart.svg'
    histogram1d = 'histogram.svg'
    histogram2d = 'hist2d.svg'
    line = 'linechart.svg'
    vlines = 'vlinechart.svg'
    bind = 'link5.svg'


@decorators.memoize
def create_icon(icon_name):
    """
    Create icon given its name.
    :param icon_name: Given from the Icons-class.
    :return: QIcon.
    """
    if icon_name is None:
        return EMPTY_ICON
    filename = '{}/svg_icons/{}'.format(
        os.path.dirname(__file__), icon_name)
    return QtGui.QIcon(filename)
