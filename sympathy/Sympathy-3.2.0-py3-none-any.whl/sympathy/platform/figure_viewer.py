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
from sympathy.api import qt2 as qt
QtGui = qt.import_module('QtGui')
QtWidgets = qt.import_module('QtWidgets')

from .viewerbase import ViewerBase
from .widget_library import mpl_toolbar_factory


class FigureViewer(ViewerBase):
    def __init__(self, plot_data=None, console=None, parent=None):
        super().__init__(parent)
        self._figure = plot_data
        self._mpl_figure = self._figure.get_mpl_figure()
        self._canvas = self._figure._get_qtcanvas()
        self._toolbar = mpl_toolbar_factory(self._canvas, self)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._canvas)
        self._layout.addWidget(self._toolbar)
        self.setLayout(self._layout)
        self.setMinimumWidth(300)

        self._set_figure_background_color()

    def _set_figure_background_color(self):
        # FIXME: setting the correct facecolor for matplotlib figures embedded
        # in QTabWidget or QGroupBox does not work
        color = self.palette().color(self.backgroundRole())
        self._canvas.figure.set_facecolor(color.name())

    def figure(self):
        return self._figure

    def data(self):
        return self.figure()

    def update_data(self, data):
        if data is not None:
            self._figure = data
            # replace the figure in the canvas and the canvas in the figure
            self._mpl_figure = self._figure.get_mpl_figure()
            self._mpl_figure.set_canvas(self._canvas)
            self._mpl_figure._original_dpi = self._mpl_figure.dpi
            self._mpl_figure.dpi = self._canvas.figure.dpi
            self._canvas.figure = self._mpl_figure
            self._set_figure_background_color()
            self._figure.rotate_xlabels_for_dates()
            self._canvas.draw_idle()  # is needed

            # When switching between figures in the same canvas we need to make
            # sure that the new figure is resized to fit the size of the canvas.
            # This is already implemented in FigureCanvasQt.resizeEvent() so we
            # call that instead of implementing it ourselves.
            # Note that simply calling canvas.resize with the old size wouldn't
            # trigger resizeEvent.
            resize_event = QtGui.QResizeEvent(self._canvas.size(), self._canvas.size())
            self._canvas.resizeEvent(resize_event)

            from mpl_toolkits.mplot3d.axes3d import Axes3D
            for ax in self._mpl_figure.axes:
                if isinstance(ax, Axes3D):
                    ax.mouse_init()

            # Requires re-connection or interactivity is lost, since matplotlib
            # 3.4.
            self._toolbar.connect_canvas()
