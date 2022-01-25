from PySide2 import QtWidgets, QtCore

from ciomax.components import widgets


class CheckboxGrp(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super(CheckboxGrp, self).__init__()
        scale_factor = self.logicalDpiX() / 96.0

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        num_checkboxes = kwargs.get("checkboxes", 1)
        sublabels = kwargs.get("sublabels", [])

        if len(sublabels) != num_checkboxes:
            sublabels = [""] * num_checkboxes

        layout.addWidget(widgets.FormLabel(kwargs.get("label", "")))

        self.checkboxes = []

        for i in range(num_checkboxes):
            cb = QtWidgets.QCheckBox(sublabels[i])
            self.checkboxes.append(cb)
            layout.addWidget(cb)

        layout.addSpacing(scale_factor * 85)
