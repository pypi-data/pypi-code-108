from typing import List

from propsettings import configurable
from propsettings.setting import Setting
from PySide2 import QtWidgets

from propsettings_qt import setting_widget_retrieval
from propsettings_qt.object_drawers.object_drawer import ObjectDrawer


class DefaultObjectDrawer(QtWidgets.QWidget, ObjectDrawer):

    def __init__(self, parent=None):
        super(DefaultObjectDrawer, self).__init__(parent=parent)
        self._layout = QtWidgets.QFormLayout()
        self.setLayout(self._layout)

    def draw_object(self, obj):
        self.clear()
        settings = configurable.get_settings(obj)
        settings = self._sort_settings(settings)
        for stg in settings:
            stg_widget = setting_widget_retrieval.get_setting_widget(obj, stg)
            self._layout.addRow(stg.label, stg_widget)

    def clear(self):
        while self._layout.count() > 0:
            item = self._layout.itemAt(0)
            wgt = item.widget()
            if wgt:
                self._layout.removeItem(item)
                wgt.deleteLater()

    def _sort_settings(self, settings: List[Setting]):
        """
        Ordenar una lista de Settings según los tipos de datos.
        :param settings:
        :return:
        """
        settings_by_sort_order = {}
        for stg in settings:
            settings_by_sort_order.setdefault(stg.sort_order, []).append(stg)

        settings_by_sort_order = sorted(settings_by_sort_order.items(), key=lambda x: x[0])

        sorted_settings = []
        for _, settings in settings_by_sort_order:
            settings.sort(key=lambda stg: stg.label)
            for stg in settings:
                sorted_settings.append(stg)

        return sorted_settings

