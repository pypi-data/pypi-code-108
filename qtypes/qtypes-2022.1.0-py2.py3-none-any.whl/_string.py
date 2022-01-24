__all__ = ["String"]


from qtpy import QtCore, QtGui, QtWidgets

from ._base import Base
from ._signals import Signals


class Widget(Signals, QtWidgets.QLineEdit):
    pass


class String(Base):
    defaults = dict()
    defaults["value"] = ""

    def _create_widget(self):
        widget = Widget()
        widget.editingFinished.connect(self.on_editing_finished)
        return widget

    def on_editing_finished(self):
        new = self._widget.text()
        if new != self._value["value"]:
            self._value["value"] = new
            self.edited.emit(self._value)
            self.updated.emit(self._value)

    def on_updated(self, value):
        self._value.update(value)
        self._widget.setText(self._value["value"])
