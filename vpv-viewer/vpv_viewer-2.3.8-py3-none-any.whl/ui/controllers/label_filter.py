
from PyQt5 import QtGui, QtCore
from vpv.ui.views.ui_label_filter import Ui_LabelFilter


class LabelFilter(QtGui.QWidget):
    filter_label_signal = QtCore.pyqtSignal(list)

    def __init__(self, mainwindow):
        super(LabelFilter, self).__init__(mainwindow)
        self.ui = Ui_LabelFilter()
        self.ui.setupUi(self)

        self.ui.lineEditShowLabel.textChanged.connect(self.filter_label)

    def filter_label(self):
        input_ = self.ui.lineEditShowLabel.text()
        labels = input_.split(' ')
        try:
            labels = [int(x) for x in labels]
        except (TypeError, ValueError):
            labels = [0] # Reset the filtering
        self.filter_label_signal.emit(labels)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.ui.lineEditShowLabel.setFocus()

