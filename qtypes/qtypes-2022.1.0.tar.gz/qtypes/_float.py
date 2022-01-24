__all__ = ["Float"]


import math

from qtpy import QtWidgets, QtGui

from ._base import Base
from ._signals import Signals
from ._units import converter, get_valid_conversions


class Widget(Signals, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # build widget
        self.setLayout(QtWidgets.QHBoxLayout())
        self.spin_box = QtWidgets.QDoubleSpinBox()
        self.layout().addWidget(self.spin_box)
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setFixedWidth(100)
        self.combo_box.hide()  # will get shown if units are set
        self.layout().addWidget(self.combo_box)
        self.layout().setContentsMargins(0, 0, 0, 0)


class Float(Base):
    defaults = dict()
    defaults["value"] = float("nan")
    defaults["units"] = None
    defaults["minimum"] = float("-inf")
    defaults["maximum"] = float("inf")
    defaults["decimals"] = 6

    @property
    def allowed_units(self):
        out = []
        for i in range(self._widget.combo_box.count()):
            out.append(self._widget.combo_box.itemText(i))
        return out

    def _create_widget(self):
        widget = Widget()
        widget.spin_box.editingFinished.connect(self.on_edited)
        widget.combo_box.currentIndexChanged.connect(self.on_combo_changed)
        self._widget = widget
        self.on_updated(self._value)
        return widget

    def on_combo_changed(self):
        new = self._widget.combo_box.currentText()
        self.set({"units": new})

    def on_disabled(self, value: bool):
        self._widget.spin_box.setDisabled(value)
        self._widget.combo_box.setDisabled(False)

    def on_edited(self):
        new = self._widget.spin_box.value()
        if not math.isclose(self._value["value"], new):
            self._value["value"] = new
            self.edited.emit(self._value)
            self.updated.emit(self._value)

    def on_updated(self, value):
        """
        Must recieve complete and self-consistent dictionary.
        Updates state of widget
        """
        if self._widget.spin_box.hasFocus():
            return
        # value
        if math.isnan(value["value"]):
            self._widget.spin_box.setSpecialValueText("nan")
            self._widget.spin_box.setValue(self._widget.spin_box.minimum())
        else:
            self._widget.spin_box.setSpecialValueText("")
            self._widget.spin_box.setValue(value["value"])
        # units
        if value["units"] is not None and len(self.allowed_units) == 0:
            self._widget.combo_box.currentIndexChanged.disconnect(self.on_combo_changed)
            self._widget.combo_box.addItems(get_valid_conversions(value["units"]))
            self._widget.combo_box.currentIndexChanged.connect(self.on_combo_changed)
        if value["units"] is not None:
            self._widget.combo_box.show()
            self._widget.combo_box.currentIndexChanged.disconnect(self.on_combo_changed)
            self._widget.combo_box.setCurrentIndex(self.allowed_units.index(value["units"]))
            self._widget.combo_box.currentIndexChanged.connect(self.on_combo_changed)
        # minimum, maximum
        self._widget.spin_box.setMinimum(self._value["minimum"])
        self._widget.spin_box.setMaximum(self._value["maximum"])
        # tool tip
        self._widget.spin_box.setToolTip(f"minimum:{value['minimum']}\nmaximum:{value['maximum']}")
        # decimals
        self._widget.spin_box.setDecimals(self._value["decimals"])

    def set(self, value: dict):
        # TODO: diff check
        if "units" in value.keys():
            new = value["units"]
            old = self._value["units"]
            if "value" not in value.keys():
                value["value"] = converter(self._value["value"], old, new)
            new_min, new_max = sorted([converter(self._value["minimum"], old, new),
                                       converter(self._value["maximum"], old, new)])
            if "minimum" not in value.keys():
                value["minimum"] = new_min
            if "maximum" not in value.keys():
                value["maximum"] = new_max
        self._value.update(value)
        self.updated.emit(self._value)
