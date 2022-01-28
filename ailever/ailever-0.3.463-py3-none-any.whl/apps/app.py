from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from .UIAilever import Ui_MainWindow

class AileverAppEyes(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(AileverAppEyes, self).__init__(parent)
        self.setupUi(self)

def run():
    app = QApplication(sys.argv)
    form = AileverAppEyes()
    form.show()
    app.exec_()
    print(f'[AILEVER] The Eyes is sucessfully executed!')

if __name__ == '__main__':
    run()
