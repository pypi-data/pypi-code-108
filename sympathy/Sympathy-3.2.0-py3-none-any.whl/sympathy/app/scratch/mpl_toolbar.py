# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
from Qt import QtWidgets, QtGui

import matplotlib
import matplotlib.figure
import matplotlib.backends.backend_qt5agg
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)


class NavigationToolbar(NavigationToolbar):
    # Removing tools
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adding tools
        action = QtWidgets.QAction(
            QtGui.QIcon('../../resources/icons/application.ico'),
            'Add more Sympathy!')
        action.triggered.connect(self.sympathy_tool)
        self.insertAction(self.actions()[-1], action)

    def sympathy_tool(self):
        print('Win!')


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()

    fig = matplotlib.figure.Figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    canvas = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg(fig)
    toolbar = NavigationToolbar(canvas, parent=w, coordinates=True)

    layout.addWidget(canvas)
    layout.addWidget(toolbar)
    w.setLayout(layout)

    w.show()
    app.exec_()
