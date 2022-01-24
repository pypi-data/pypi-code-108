__all__ = ["Base"]


import qtpy
from qtpy import QtCore, QtGui, QtWidgets


from ._signals import Signals


class Widget(Signals, QtWidgets.QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText("this widget provided by qtypes Base class, please overload _create_widget")


class Base(QtWidgets.QTreeWidgetItem):

    def __init__(self, label="", disabled=False, value={}):
        super().__init__([label, ""])
        self._value = self.defaults.copy()
        self._value.update(value)
        self._widget = self._create_widget()
        self.children = []
        # signals and slots
        self.updated.connect(self.on_updated)
        self.updated.emit(self._value)
        self.disabled.connect(self.on_disabled)
        self.disabled.emit(disabled)

    def __getitem__(self, index):
        if index < 0:
            index = self.childCount() + index
        return self.child(index)

    def append(self, item):
        self.addChild(item)
        if isinstance(item, Base):
            widget = item._widget
            widget.setParent(self.treeWidget())
            self.treeWidget().setItemWidget(item, 1, widget)
            self.children.append(item)

    def _create_widget(self):
        return Widget()

    @property
    def disabled(self):
        return self._widget.disabled

    @property
    def edited(self):
        return self._widget.edited

    def get(self) -> dict:
        return self._value

    def get_value(self) -> object:
        return self._value["value"]

    @property
    def label(self):
        return self.text(0)

    @label.setter
    def label(self, value: str):
        self.setText(0, value)

    def on_disabled(self, value: bool):
        self._widget.setDisabled(value)

    def on_updated(self, value: dict):
        raise NotImplementedError

    def set(self, value: object):
        # TODO: diff check
        self._value.update(value)
        self.updated.emit(self._value)

    def set_value(self, value: object):
        if value != self._value["value"]:
            self._value["value"] = value
            self.updated.emit(self._value)

    @property
    def updated(self):
        return self._widget.updated
