from PySide2 import QtWidgets, QtCore

from propsettings.setting import Setting
from propsettings.setting_types.selectable_setting_type import Selectable
from propsettings_qt.setting_drawers.setting_drawer import SettingDrawer


class SelectableSettingDrawer(SettingDrawer):

    def __init__(self, selectable: Selectable, setting_owner, setting: Setting):
        super(SelectableSettingDrawer, self).__init__(setting_owner, setting)
        self._selectable = selectable

        self._selectable_widget = SelectableWidget(self, selectable)
        self._selectable_widget.signal_option_selected.connect(self._on_option_selected)
        self._selectable_widget.populate_options()

    def get_widget(self):
        return self._selectable_widget

    def _on_option_selected(self, option_name: str, option_data: object):
        self._set_value(option_data)
        self._selectable.call_selected_callback(self._setting_owner, option_name, option_data)


class SelectableWidget(QtWidgets.QComboBox):
    signal_option_selected = QtCore.Signal(str, object)

    def __init__(self, handler: SelectableSettingDrawer, selectable: Selectable, *args, **kwargs):
        super(SelectableWidget, self).__init__(*args, **kwargs)
        self._handler = handler
        self._selectable = selectable
        self.currentIndexChanged.connect(self._selection_changed)

    def populate_options(self):
        options = self._selectable.options
        for option_name, option_data in options:
            self.addItem(option_name, option_data)

    def _selection_changed(self, index):
        option_name, option_data = self._selectable.options[index]
        self.signal_option_selected.emit(option_name, option_data)
