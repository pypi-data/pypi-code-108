from qtpy import QtGui, QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal

from . import kerberos
from ._qt import load_ui


class DialogOverlayWidget(QtWidgets.QWidget):

    def __init__(self, dialog, parent=None):
        super().__init__(parent)

        # make the window frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)

        self.fillColor = QtGui.QColor(30, 30, 30, 120)
        self.dialog_fillColor = QtGui.QColor(240, 240, 240, 255)

        self.dialog = dialog

        try:
            self.done = self.dialog.done
            self.done.connect(self.close)
        except AttributeError:
            pass

        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.dialog)
        vbox.addItem(hbox)
        vbox.setContentsMargins(30, 30, 30, 30)
        self.setLayout(vbox)

        self.move(0, 0)
        self.resize(parent.width(), parent.height())

    def _get_dialog_xy(self):
        s = self.size()
        ds = self.dialog.size()
        dx = int(s.width()/2 - ds.width()/2)
        dy = int(s.height()/2 - ds.height()/2)
        return dx, dy

    def paintEvent(self, event):
        # this method draws the contents of the window.

        # get current window, dialog size
        s = self.size()
        ds = self.dialog.size()
        dx, dy = self._get_dialog_xy()

        # paint full window fill
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setBrush(self.fillColor)
        qp.drawRect(0, 0, s.width(), s.height())

        # draw dialog background
        qp.setBrush(self.dialog_fillColor)
        qp.drawRoundedRect(dx, dy, ds.width(), ds.height(), 5, 5)

        qp.end()


class NDSAuthDialog(*load_ui('dialog_nds_auth.ui')):

    done = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.passwordEntry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordEntry.textChanged.connect(self._update_buttons)
        self.usernameEntry.textChanged.connect(self._update_buttons)
        self.passwordEntry.returnPressed.connect(self._done)
        self.buttonBox.clicked.connect(self._done)
        self.buttonBox.buttons()[0].setEnabled(False)
        self.usernameEntry.selectAll()
        self.errorLabel.hide()
        self.errorLabel.setStyleSheet(
            "background-color: red; font-weight: bold;")
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def _update_buttons(self):
        if self.usernameEntry.text() and self.passwordEntry.text():
            self.buttonBox.buttons()[0].setEnabled(True)
        else:
            self.buttonBox.buttons()[0].setEnabled(False)

    def _done(self, button=None):
        if button and \
           self.buttonBox.buttonRole(button) == self.buttonBox.RejectRole:
            self.done.emit(False)
            return
        try:
            kerberos.kinit(
                username=self.usernameEntry.text(),
                password=self.passwordEntry.text(),
            )
        except Exception:
            self.errorLabel.show()
            return
        self.done.emit(True)



class NDSOnTapeDialog(*load_ui('dialog_nds_ontape.ui')):

    done = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.buttonBox.clicked.connect(self._done)
        self.buttonBox.setFocus()
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def _done(self, button=None):
        if button and \
           self.buttonBox.buttonRole(button) == self.buttonBox.RejectRole:
            self.done.emit(False)
            return
        self.done.emit(True)
