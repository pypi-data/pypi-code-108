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


class MidPan(QtWidgets.QGraphicsView):
    """This widget is used for debugging middle button panning."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(600, 600)
        self.setWindowTitle('MidPan')

        # Add a reference blob:
        self._blob = QtWidgets.QGraphicsEllipseItem(0, 0, 100, 100)
        self.scene().addItem(self._blob)
        self._pan_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            print("start:", event.pos())
            self._pan_pos = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
        else:
            print("other press:", event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan_pos is not None:
            print("move:", event.pos())
            offset = self._pan_pos - event.pos()
            self._pan_pos = event.pos()
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + offset.x())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self._end_pan()
        super().mouseReleaseEvent(event)

    def focusOutEvent(self, event):
        self._end_pan()
        super().focusOutEvent(event)

    # def event(self, event):
    #     event_type = event.type()
    #     if event_type in [QtCore.QEvent.Type.Leave,
    #                       QtCore.QEvent.Type.Enter,
    #                       QtCore.QEvent.WindowActivate,
    #                       QtCore.QEvent.WindowDeactivate,
    #                       QtCore.QEvent.WindowBlocked,
    #                       QtCore.QEvent.WindowUnblocked,
    #                       QtCore.QEvent.FocusIn,
    #                       QtCore.QEvent.FocusOut]:
    #         self._end_pan()
    #     super().event(event)

    def _end_pan(self):
        print("end")
        self._pan_pos = None
        self.setCursor(QtCore.Qt.ArrowCursor)

    # Let's try to add an annoying dialog to make sure that pan mode ends when
    # it should:
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C:
            picker = QtWidgets.QColorDialog()
            res = picker.exec_()
            if res == QtWidgets.QDialog.Accepted:
                self._blob.setBrush(picker.currentColor())


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    s = QtWidgets.QGraphicsScene()
    s.setSceneRect(-500, -500, 1000, 1000)
    w = MidPan(s)
    w.show()
    app.exec_()
