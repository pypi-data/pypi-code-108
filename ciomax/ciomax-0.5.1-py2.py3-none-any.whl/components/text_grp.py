from PySide2 import QtWidgets, QtCore

from ciomax.components import widgets


class TextGrp(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super(TextGrp, self).__init__()

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(widgets.FormLabel(kwargs.get("label", "")))

        self.text = QtWidgets.QLabel()

        layout.addWidget(self.text)
