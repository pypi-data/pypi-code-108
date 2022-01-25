# Created by matveyev at 23.02.2021

from PyQt5 import QtWidgets

from onlinexml_editor.gui.columns_selector_ui import Ui_ColumnSelector
import onlinexml_editor.headers as headers

persistent_columns = ('name', 'active', 'device', 'comment')


# ----------------------------------------------------------------------
class ColumnSelector(QtWidgets.QDialog):

    def __init__(self):
        super(ColumnSelector, self).__init__()

        self._ui = Ui_ColumnSelector()
        self._ui.setupUi(self)

        headers.possible_headers.sort()

        self.chk_boxes = []
        for header in headers.possible_headers[::-1]:
            if header not in persistent_columns:
                chk_box = QtWidgets.QCheckBox(str(header), self)
                chk_box.setChecked(header in headers.online_headers)
                self._ui.verticalLayout.insertWidget(0, chk_box, 0)
                self.chk_boxes.append((header, chk_box))

    # ----------------------------------------------------------------------
    def accept(self):
        online_headers = list(persistent_columns[:-1])
        new_headers = []
        for name, chk_box in self.chk_boxes:
            if chk_box.isChecked():
                new_headers.append(name)

        new_headers.sort()
        online_headers += new_headers
        online_headers.append(persistent_columns[-1])

        headers.online_headers = (tuple(online_headers))
        super(ColumnSelector, self).accept()