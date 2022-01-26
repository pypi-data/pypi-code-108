from PySide2 import QtWidgets
from propsettings.setting import Setting
from propsettings.setting_types import list_setting_type
from propsettings_qt import setting_widget_retrieval

from propsettings_qt.setting_drawers.setting_drawer import SettingDrawer


class ListSettingDrawer(SettingDrawer):

    def __init__(self, list_setting_type: list_setting_type.List, setting_owner, setting: Setting):
        super().__init__(setting_owner=setting_owner, setting=setting)
        # validar tipo de dato de la configuración (setting)
        st = self._setting_type
        if st != list:
            raise TypeError(f'Wrong setting type: {st}. Setting must be of type list.')
        self._setting_type = list_setting_type

    def get_widget(self):
        pass


class SettingsList(QtWidgets.QWidget):

    def __init__(self, list_setting_type: list_setting_type.List, handler: ListSettingDrawer, parent=None):
        super(SettingsList, self).__init__(parent=parent)
        self._handler = handler

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._list_widget = QtWidgets.QListWidget()

        self._buttons_widget = QtWidgets.QWidget()
        self._buttons_widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._buttons_widget.setLayout(buttons_layout)

        self._add_button = QtWidgets.QPushButton(text="+")
        self._remove_button = QtWidgets.QPushButton(text="-")
        self._add_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self._remove_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self._add_button)
        buttons_layout.addWidget(self._remove_button)

    def _add_element(self, element):
        index = 0

        def getter(instance: list):
            return instance[index]

        def setter(instance: list, value):
            instance[index] = value

        stg = Setting(fget=getter, fset=setter, setting_type=setting_type)
        widget = setting_widget_retrieval.get_setting_widget(l, stg)
