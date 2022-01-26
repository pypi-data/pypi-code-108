from typing import Optional

from PySide2 import QtWidgets

from propsettings_qt import setting_widget_retrieval


class SettingsAreaWidget(QtWidgets.QFrame):
    """
    Widget que muestra las configuraciones de un objeto y permite editarlas.
    """

    def __init__(self, parent=None):
        super(SettingsAreaWidget, self).__init__(parent=parent)
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self._children_count: int = 0
        self._object_drawer: Optional[QtWidgets.QWidget] = None

    @property
    def children_count(self) -> int:
        return self._children_count

    def populate_object(self, obj):
        """
        Quitar todos los elementos existentes e incializar los widgets de cada Setting de un objeto.
        :param obj:
        :return:
        """
        self.clear()
        self._object_drawer = setting_widget_retrieval.get_object_drawer(obj)
        self._layout.addWidget(self._object_drawer)

        self._children_count = self._get_widget_children_count(self._object_drawer)
        if self._children_count > 0:
            self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        else:
            self.setFrameStyle(QtWidgets.QFrame.NoFrame)

    def _get_widget_children_count(self, widget: QtWidgets.QWidget):
        children_count = 0
        children = widget.children()
        for child in children:
            if isinstance(child, QtWidgets.QWidget):
                children_count += 1
        return children_count

    def clear(self):
        while self._layout.count() > 0:
            item = self._layout.itemAt(0)
            wgt = item.widget()
            if wgt:
                self._layout.removeItem(item)
                wgt.deleteLater()
        self._children_count = 0
