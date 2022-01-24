__all__ = ["Integer"]


from qtpy import QtWidgets, QtGui

from ._base import Base
from ._signals import Signals


class Widget(Signals, QtWidgets.QSpinBox):
    pass


class Integer(Base):
    defaults = dict()
    defaults["value"] = 0
    defaults["minimum"] = -2**31
    defaults["maximum"] = 2**31 - 1

    def _create_widget(self):
        widget = Widget()
        widget.editingFinished.connect(self.on_edited)
        return widget

    def on_edited(self):
        if self._widget.value() != self._value["value"]:
            self._value["value"] = self._widget.value()
            self.edited.emit(self._value)
            self.updated.emit(self._value)

    def on_updated(self, value):
        # minimum, maximum
        self._widget.setMinimum(self._value["minimum"])
        self._widget.setMaximum(self._value["maximum"])
        # value
        self._widget.setValue(self._value["value"])
        # tool tip
        self._widget.setToolTip(f"minimum:{value['minimum']}\nmaximum:{value['maximum']}")
