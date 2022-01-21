
#from PySide2 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)

import main_paras

def handleVisibleChanged():
    
    if not QtGui.QGuiApplication.inputMethod().isVisible():
        print('keybord close')
        return
    print('keybord up')
    main_paras.keyboard_up.signal.emit('keyboard')
    for w in QtGui.QGuiApplication.allWindows():
        if w.metaObject().className() == "QtVirtualKeyboard::InputView":
            keyboard = w.findChild(QtCore.QObject, "keyboard")
            if keyboard is not None:
                r = w.geometry()
                r.moveTop(keyboard.property("y"))
                w.setMask(QtGui.QRegion(r))
                return


def main():
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    app = QtWidgets.QApplication(sys.argv)

    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)

    w = QtWidgets.QLineEdit()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    
