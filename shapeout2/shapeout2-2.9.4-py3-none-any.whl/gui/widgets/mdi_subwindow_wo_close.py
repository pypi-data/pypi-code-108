from PyQt5 import QtCore, QtWidgets


class MDISubWindowWOButtons(QtWidgets.QMdiSubWindow):
    def __init__(self, *args, **kwargs):
        super(MDISubWindowWOButtons, self).__init__(*args, **kwargs)
        self.setSystemMenu(None)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint
                            | QtCore.Qt.WindowTitleHint)

    def closeEvent(self, event):
        event.ignore()
