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

import os.path

from matplotlib import colors as mpl_colors

from sylib.figure import colors
from sylib.report import decorators

from Qt import QtGui
from Qt import QtWidgets


SIZE = 26
EMPTY_ICON = QtGui.QIcon()


class SvgIcon(object):
    blank = None
    angle = 'angle.svg'
    arrow = 'arrow.svg'
    vert_align = 'vert_align.svg'
    horz_align = 'horz_align.svg'
    invalid = 'ban-circle-symbol.svg'
    data = 'data3.svg'
    chat = 'chat51.svg'
    graph = 'ascending7.svg'
    plot = 'view-plot-axes-symbolic.svg'
    coordinates = '3d76.svg'
    projection = 'textile.svg'
    percentage = 'percentage.svg'
    plug = 'energy7.svg'
    x_axis = 'view-xaxis-symbolic.svg'
    y_axis = 'view-yaxis-symbolic.svg'
    z_axis = 'view-zaxis-symbolic.svg'
    n_axis = 'view-naxis-symbolic.svg'
    x_axis_pos_bottom = 'view-xaxis-bottom-symbolic.svg'
    x_axis_pos_top = 'view-xaxis-top-symbolic.svg'
    y_axis_pos_left = 'view-yaxis-left-symbolic.svg'
    y_axis_pos_right = 'view-yaxis-right-symbolic.svg'
    axes_bottom_left = 'view-axes-bottom-left-symbolic.svg'
    axes_bottom_right = 'view-axes-bottom-right-symbolic.svg'
    axes_top_left = 'view-axes-top-left-symbolic.svg'
    axes_top_right = 'view-axes-top-right-symbolic.svg'
    x_data = 'x-data-symbolic.svg'
    y_data = 'y-data-symbolic.svg'
    z_data = 'z-data-symbolic.svg'
    width = 'width3.svg'
    height = 'height6.svg'
    rotate = 'rotate.svg'
    rounded_rectangle = 'rounded_rectangle.svg'
    layers = 'layers.svg'
    layer = 'layer.svg'
    link = 'link5.svg'
    view = 'personal5.svg'
    ruler = 'ruler.svg'
    scales = 'scales2.svg'
    triangle = 'set1.svg'
    layout = 'layout.svg'
    text = 'label.svg'
    text_size = 'text-size.svg'
    location = 'location.svg'
    frame = 'frame-on-off.svg'
    number_columns = 'number_columns.svg'
    aspect_ratio = 'view-plot-aspect-ratio-symbolic.svg'
    ticks = 'view-plot-axes-ticks.svg'
    config = 'three115.svg'
    label = 'tag31.svg'
    labels = 'labels.svg'
    aspect = 'view-aspect-symbolic.svg'
    color = 'view-color-symbolic.svg'
    alpha = 'view-alpha-symbolic.svg'
    linewidth = 'view-linewidth-symbolic.svg'
    linestyle = 'view-linestyle-symbolic.svg'
    drawstyle = 'view-drawstyle-symbolic.svg'
    hatch_pattern = 'hatch-pattern.svg'
    histtype = 'view-histtype-symbolic.svg'
    marker = 'view-marker-symbolic.svg'
    markersize = 'view-markersize-symbolic.svg'
    bin_min_edge = 'view-bin-min-edge-symbolic.svg'
    bin_max_edge = 'view-bin-max-edge-symbolic.svg'
    barwidth = 'view-bar-width-symbolic.svg'
    barlabelvalgin = 'view-valign-symbolic.svg'
    bar_grouping = 'view-grouping-symbolic.svg'
    colorbar_orientation = 'view-plot-colorbar-orientation-symbolic.svg'
    colorbar_min = 'view-plot-colorbar-min-symbolic.svg'
    colorbar_max = 'view-plot-colorbar-max-symbolic.svg'
    limit = 'view-limit-symbolic.svg'
    list = 'list23.svg'
    pages = 'copy9.svg'
    page = 'page.svg'
    grid = 'view-plot-grid-symbolic.svg'
    legend = 'view-plot-legend-symbolic.svg'
    visible = 'eye-open.svg'
    invisible = (
        'eye-with-a-diagonal-line-interface-symbol-for-invisibility.svg')
    python = 'python-logo.svg'
    python_grayscale = 'python-logo-grayscale.svg'
    plus = 'add133.svg'
    minus = 'minus75.svg'
    picture = 'image.svg'
    show_frame = 'view-plot-frame-visibility.svg'
    boxplot = 'boxplot.svg'
    piechart = 'piechart.svg'
    piechart_explode = 'piechart_explode.svg'
    piechart_shadow = 'piechart_shadow.svg'
    diameter = 'diameter.svg'
    errorbar = 'errorbar.svg'
    ypos = 'ypos.svg'
    timeline = 'timeline.svg'
    imageplot = 'imageplot.svg'
    template = 'template.svg'
    wrench = 'wrench-solid.svg'
    tools = 'tools-solid.svg'
    template = 'file-and-wand.svg'
    info = 'info-circle-solid.svg'
    custom_plot = 'custom_plot.svg'
    bar_wizard = 'bar_wizard.svg'
    box_wizard = 'box_wizard.svg'
    pie_wizard = 'pie_wizard.svg'
    line_wizard = 'line_wizard.svg'
    hist_wizard = 'hist_wizard.svg'
    image_wizard = 'image_wizard.svg'
    heatmap_wizard = 'heatmap_wizard.svg'
    scatter_wizard = 'scatter_wizard.svg'
    timeline_wizard = 'timeline_wizard.svg'
    # Icons for layers:
    scatter = 'view-plot-scatter-symbolic.svg'
    bar = 'view-plot-bar-symbolic.svg'
    histogram1d = 'view-plot-hist-symbolic.svg'
    heatmap = 'view-plot-heatmap-symbolic.svg'
    line = 'view-plot-line-symbolic.svg'
    lines = 'view-plot-lines-symbolic.svg'
    barcontainer = 'view-plot-barcontainer-symbolic.svg'
    histcontainer = 'view-plot-histcontainer-symbolic.svg'
    iterator = 'view-plot-iterator-symbolic.svg'
    vlines = 'vlinechart.svg'
    bind = 'link5.svg'
    rectangles = 'rectangles.svg'
    ellipses = 'ellipses.svg'
    filled = 'filled.svg'
    # control icons:
    edit = 'edit-pencil.svg'
    copy = 'copy9.svg'
    delete = 'edit-trash-symbolic.svg'
    back = 'arrow-left-solid.svg'
    # logic
    and_ = 'and.svg'
    or_ = 'or.svg'
    # query
    field = 'query-field.svg'
    arrayfield = 'query-arrayfield.svg'
    importquery = 'query-importquery.svg'


@decorators.memoize
def create_icon(icon_name):
    """
    Create icon given its name.
    :param icon_name: Given from the Icons-class.
    :return: QIcon.
    """
    if icon_name is None:
        return EMPTY_ICON

    if os.path.isabs(icon_name):
        filename = icon_name
    else:
        filename = '{}/svg_icons/{}'.format(
            os.path.dirname(__file__), icon_name)
    return QtGui.QIcon(filename)


@decorators.memoize
def color_icon(color):
    """
    Create filled icon with given color.
    Parameters
    ----------
    color : list or tuple or str or unicode

    Returns
    -------
    QIcon
    """
    color = colors.parse_to_mpl_color(color)
    if color is None:
        return create_icon(SvgIcon.color)
    rgbf_color = mpl_colors.colorConverter.to_rgb(color)
    qim = QtGui.QImage(SIZE, SIZE, QtGui.QImage.Format_ARGB32)
    qim.fill(QtGui.QColor.fromRgbF(*rgbf_color))
    pixmap = QtGui.QPixmap.fromImage(qim)
    return QtGui.QIcon(pixmap)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    icon = color_icon('#fefe22')
    widget = QtWidgets.QPushButton()
    widget.setIcon(icon)
    widget.show()
    widget.raise_()

    app.exec_()
