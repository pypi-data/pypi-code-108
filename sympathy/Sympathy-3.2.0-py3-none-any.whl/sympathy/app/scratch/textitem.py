# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
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
import Qt.QtWidgets as QtWidgets
import Qt.QtCore as QtCore


class GraphicsTextItem(QtWidgets.QGraphicsTextItem):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setPlainText('\n'.join(['a ' * 255] * 255))

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 400, 400)


class GraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setSceneRect(QtCore.QRectF(0, 0, 400, 400))


class GraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._scene = GraphicsScene(parent=self)
        self.setScene(self._scene)
        self._text_item = GraphicsTextItem()
        self._scene.addItem(self._text_item)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    v = GraphicsView()
    v.show()
    app.exec_()
