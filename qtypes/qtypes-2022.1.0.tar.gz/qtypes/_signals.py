from qtpy import QtCore, QtGui, QtWidgets


class Signals():
    disabled = QtCore.Signal(bool)
    edited = QtCore.Signal(dict)  # when user is finished editing widget
    updated = QtCore.Signal(dict)  # any time value changes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disabled.connect(self._on_disabled)

    def _on_disabled(self, value):
        self.setDisabled(value)
