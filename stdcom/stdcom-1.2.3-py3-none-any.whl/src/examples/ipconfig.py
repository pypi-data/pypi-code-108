#  Copyright (C) 2021 Vremsoft LLC and/or its subsidiary(-ies).
#  All rights reserved.
#  Contact: Laura Chapman  (edc@vremsoft.com)
#  Commercial Usage
#  Licensees holding valid Vremsoft LLC licenses may use this file in
#  accordance with the License Agreement provided with the
#  Software or, alternatively, in accordance with the terms contained in
#  a written agreement between you and Vremsoft. LLC
#

from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import pyqtSlot, pyqtSignal



import  sys, os

if __name__=="__main__":

    current = os.path.dirname(os.path.realpath(__file__))

    # Getting the parent directory name
    # where the current directory is present.
    parent = os.path.dirname(current)

    # adding the parent directory to
    # the sys.path.
    sys.path.append(parent)

    import stdcomqt5widget

    def callBack(ip, port):
        print("Address: ", ip, " Service Port: ", port)

    app = QApplication(sys.argv)
    w = stdcomqt5widget.ipconfigDialog(callBack)
    w.show()
    sys.exit(app.exec_())
