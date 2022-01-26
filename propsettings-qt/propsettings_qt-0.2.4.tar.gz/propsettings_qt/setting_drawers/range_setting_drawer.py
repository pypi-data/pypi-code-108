from PySide2 import QtWidgets, QtCore, QtGui

from propsettings.setting import Setting
from propsettings.setting_types.range_setting_type import Range
from propsettings_qt.setting_drawers.setting_drawer import SettingDrawer
from propsettings_qt.widgets.float_slider import FloatSlider


class RangeSettingDrawer(SettingDrawer):

    def __init__(self, value_range: Range, setting_owner, setting: Setting):
        super(RangeSettingDrawer, self).__init__(setting_owner, setting)
        self._range = value_range

        self._widget = RangeSlider(self, self._range)
        self._widget.set_value(self._get_value())
        self._widget.signal_value_changed.connect(self._set_value)

    def get_widget(self):
        return self._widget


class RangeSlider(QtWidgets.QSplitter):

    signal_value_changed = QtCore.Signal(float)

    def __init__(self, handler: RangeSettingDrawer, value_range: Range, *args, **kwargs):
        super(RangeSlider, self).__init__(*args, **kwargs)
        self._handler = handler
        self._range = value_range

        self._edit = QtWidgets.QLineEdit()

        if self._is_float():
            self._slider = FloatSlider(orientation=QtCore.Qt.Horizontal)
            self._slider.floatValueChanged.connect(self._on_slider_changed)
            self._edit.setValidator(QtGui.QDoubleValidator())
        else:
            self._slider = QtWidgets.QSlider(orientation=QtCore.Qt.Horizontal)
            self._slider.valueChanged.connect(self._on_slider_changed)
            self._edit.setValidator(QtGui.QIntValidator())

        self._slider.setMinimum(self._range.min)
        self._slider.setMaximum(self._range.max)

        self._edit.editingFinished.connect(self._on_edit_changed)

        self.addWidget(self._slider)
        self.addWidget(self._edit)

    def set_value(self, value):
        value = self._clamp_value(value)
        self._set_slider_value(value)
        self._set_edit_value(value)

    def _set_slider_value(self, value):
        self._slider.setValue(value)

    def _set_edit_value(self, value):
        self._edit.setText(f'{value}'[:5])

    def _on_slider_changed(self, value):
        value = self._clamp_value(value)
        self._set_edit_value(value)
        self.signal_value_changed.emit(value)

    def _on_edit_changed(self):
        value = self._get_value_from_edit()
        value = self._clamp_value(value)
        self._set_slider_value(value)
        self.signal_value_changed.emit(value)

    def _get_value_from_edit(self):
        """
        Obtener valor a partir del string editado en el campo de edición
        :return:
        """
        value = self._edit.text()
        if self._is_float():
            return float(value)
        else:
            return int(value)

    def _is_float(self) -> bool:
        min_is_float = isinstance(self._range.min, float)
        max_is_float = isinstance(self._range.max, float)
        return min_is_float or max_is_float

    def _clamp_value(self, value):
        value = min(self._range.max, max(self._range.min, value))
        return value
