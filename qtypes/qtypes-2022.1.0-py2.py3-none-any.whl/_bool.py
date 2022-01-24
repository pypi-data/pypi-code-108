__all__ = ["Bool"]


from qtpy import QtCore, QtGui, QtWidgets

from ._base import Base
from ._signals import Signals


class Widget(Signals, QtWidgets.QCheckBox):
    pass


class Bool(Base):
    defaults = dict()
    defaults["value"] = False

    def _create_widget(self):
        widget = Widget()
        widget.stateChanged.connect(self.on_state_changed)
        return widget

    def on_state_changed(self, new):
        self._value["value"] = bool(new)
        self.edited.emit(self._value)
        self.updated.emit(self._value)

    def on_updated(self, value):
        self._widget.stateChanged.disconnect(self.on_state_changed)
        self._value.update(value)
        self._widget.setChecked(self._value["value"])
        self._widget.stateChanged.connect(self.on_state_changed)

