from PyQt5 import QtCore, QtGui, QtWidgets

class EmitThread(QtCore.QThread):

    signal= QtCore.pyqtSignal(object)

    def __init__(self, sharedQue):
        QtCore.QThread.__init__(self)
        self.qForGui=sharedQue

    def run(self):
        print("Start emit thread")
        while True:
            qItem=self.qForGui.get()
            print("In EmitThread, got from que",qItem)
            self.signal.emit(qItem)
            self.qForGui.task_done()
