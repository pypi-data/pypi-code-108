__all__ = ["Enum"]


from qtpy import QtCore, QtGui, QtWidgets

from ._base import Base
from ._signals import Signals


class Widget(Signals, QtWidgets.QComboBox):
    pass


class Enum(Base):
    defaults = dict()
    defaults["value"] = ""
    defaults["allowed"] = [""]

    def _create_widget(self):
        widget = Widget()
        widget.currentTextChanged.connect(self.on_current_text_changed)
        self._widget = widget
        self.on_updated(self._value)
        return widget

    def on_current_text_changed(self, new):
        self._value["value"] = new
        self.edited.emit(self._value)
        self.updated.emit(self._value)

    def on_updated(self, value):
        self._widget.currentTextChanged.disconnect(self.on_current_text_changed)

        # allowed
        all_items = [self._widget.itemText(i) for i in range(self._widget.count())]
        if self._value["allowed"] != all_items:
            self._widget.clear()
            self._widget.addItems(self._value["allowed"])
        # value
        if self._value["value"] not in self._value["allowed"]:
            self._value["value"] = self._value["allowed"][0]
        index = self._value["allowed"].index(self._value["value"])
        self._widget.setCurrentIndex(index)

        self._widget.currentTextChanged.connect(self.on_current_text_changed)
