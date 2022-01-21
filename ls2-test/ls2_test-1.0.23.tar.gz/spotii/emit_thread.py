from PyQt5 import QtCore
class SignalThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)
    

class PageParking(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)

    
##    def __init__(self, parent=None):
##        super(_EmitThread, self).__init__(parent)
##        self.signal.connect(self.signalHandler)
##        self.running = True
##    def signalHandler(self, item):
##        if isinstance(item, str) == True:
##            print(item," is tring")
##            if item == 'close':
##                print("close now")
##                self.running = False
##        elif isinstance(item, list) == True:
##            print(item," is list")
##        else:
##            print(itme," is unknown type")
##    def run(self):              
##        print("Start _Emit")
##        while self.running:
##            pass
##        print("_Emit thread end")


