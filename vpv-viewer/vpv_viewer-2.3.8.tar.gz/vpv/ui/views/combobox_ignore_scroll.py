from PyQt5 import QtGui, QtCore

class QComboBoxIgnoreSCroll(QtGui.QComboBox):

    def __init__(self, scrollWidget=None, *args, **kwargs):
        super(QComboBoxIgnoreSCroll, self).__init__(*args, **kwargs)
        self.scrollWidget=scrollWidget
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Wheel:
            return True
        return super(QComboBoxIgnoreSCroll, self).eventFilter(obj, event)
