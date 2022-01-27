from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog
from vpv.ui.views.ui_log_viewer import Ui_Dialog
from vpv.common import error_dialog


class Logview(QDialog):
    def __init__(self, parent, log_file):
        super(Logview, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.log_file = log_file

        self.ui.pushButtonClose.clicked.connect(self.close)
        self.ui.pushButtonCopyText.clicked.connect(self.copy_text)
        self.ui.pushButtonClearLog.clicked.connect(self.clear_log)

        try:
            with open(log_file, 'r') as fh:
                lines = fh.readlines()
        except (IOError, FileNotFoundError) as e:
            error_dialog(parent, "Cannot open logfile", log_file)
            return

        self.log_text = ''.join(lines)
        self.ui.textBrowser.setPlainText(self.log_text)
        self.show()

    def copy_text(self):
        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.log_text, mode=cb.Clipboard)

    def clear_log(self):
        open(self.log_file, 'w').close()
        self.ui.textBrowser.setPlainText("")