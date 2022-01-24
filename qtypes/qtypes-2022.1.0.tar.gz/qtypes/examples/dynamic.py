"""Example of an interface to typical daemons on the Wright Group fs system"""


import sys
import functools
import random


import qtypes
from qtpy import QtWidgets, QtGui
from qtypes._base import Base


class MyMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("dynamic")
        self.tree_widget = qtypes.TreeWidget()

        allowed = ["choose", "TODO"]
        self.add_item_enum = qtypes.Enum("add item", value={"value":"choose", "allowed":allowed})
        self.tree_widget.append(self.add_item_enum)

        self.setCentralWidget(self.tree_widget)


def dynamic():
    app = QtWidgets.QApplication(sys.argv)
    widget = MyMainWindow()
    widget.show()
    app.exec_()


if __name__ == "__main__":
    dynamic()
