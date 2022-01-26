from QtSLIX import MainWindow
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication([])
    window = MainWindow.MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
