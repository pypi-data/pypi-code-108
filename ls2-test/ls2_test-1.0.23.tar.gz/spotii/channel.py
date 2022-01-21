# from emit_thread import _EmitThread
# class Channel():
#     _thread = _EmitThread()
#     def hook(self, guard):
#         self._thread.signal.connect(guard)
#         self._thread.start()
#     def notify(self, item):
#         self._thread.signal.emit(item)



# from PyQt5 import QtCore
# class Channel(QtCore.QThread):
#     signal = QtCore.pyqtSignal(object)
#     def hook(self, guard):
#         self.signal.connect(guard)
#     def notify(self, item):
#         self.signal.emit(item)
