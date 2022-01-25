from PySide2 import QtWidgets, QtCore

from ciomax.components import widgets


class IntFieldGrp(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super(IntFieldGrp, self).__init__()

        self.hidable = kwargs.get("hidable")
        self.enablable = kwargs.get("enablable")
        if self.hidable:
            self.enablable = False


        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(widgets.FormLabel(kwargs.get("label", "")))

        # hidable checkbox
        if self.hidable or self.enablable:
            self.display_checkbox = QtWidgets.QCheckBox()
            layout.addWidget(self.display_checkbox)
            self.display_checkbox.stateChanged.connect(self.set_active)

        # field
        self.field = QtWidgets.QSpinBox()
        if kwargs.get("minimum") is not None:
            self.field.setMinimum(kwargs.get("minimum"))
        if kwargs.get("maximum") is not None:
            self.field.setMaximum(kwargs.get("maximum"))
            
        self.field.setSingleStep(kwargs.get("step", 1))
        self.field.setValue(kwargs.get("default", 0))
        layout.addWidget(self.field)

        # optional checkbox
        self.checkbox = widgets.add_checkbox(
            layout,
            kwargs.get("checkbox"),
            kwargs.get("check_label", "")
        )

    def set_active(self, value=None):
        if not (self.hidable or self.enablable):
            return
        if self.hidable:
            self._show() if value else self._hide()

        self._enable() if value else self._disable()


    def _hide(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.hide()
        if self.checkbox:
            self.checkbox.hide()

    def _show(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.show()
        if self.checkbox:
            self.checkbox.show()

    def _disable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.setEnabled(False)
        if self.checkbox:
            self.checkbox.setEnabled(False)

    def _enable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.setEnabled(True)
        if self.checkbox:
            self.checkbox.setEnabled(True)

