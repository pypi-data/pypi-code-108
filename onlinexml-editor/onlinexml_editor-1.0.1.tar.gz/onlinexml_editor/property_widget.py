# Created by matveyev at 26.01.2021

from PyQt5 import QtWidgets, QtCore
from onlinexml_editor.gui.property_ui import Ui_Property

# ----------------------------------------------------------------------
class PropertyWidget(QtWidgets.QWidget):
    delete_me = QtCore.pyqtSignal(int)

    # ----------------------------------------------------------------------
    def __init__(self, parent, id, name='', value='', is_part_of_serial=False):
        super(PropertyWidget, self).__init__(parent)
        self._id = id

        self._ui = Ui_Property()
        self._ui.setupUi(self)
        self._ui.le_name.setText(name)
        self._ui.le_name.setEnabled(not is_part_of_serial)
        if is_part_of_serial and name == 'device':
            self._ui.cmd_delete.setEnabled(False)

        self._ui.le_value.setText(value)

        self._ui.cmd_delete.clicked.connect(lambda checked, x=self._id: self.delete_me.emit(x))

    # ----------------------------------------------------------------------
    def get_data(self):
        if self._ui.le_name.text() != '' and self._ui.le_value.text() != '':
            return True, self._ui.le_name.text(), self._ui.le_value.text()
        else:
            return False, None, None