"""Example of an interface to typical daemons on the Wright Group fs system"""


import sys


import qtypes
from qtpy import QtWidgets, QtGui
from qtypes._base import Base


class MyMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("qtypes fs test")

        self.tree_widget = qtypes.TreeWidget()
        self.tree_widget.append(qtypes.String("string"))
        self.tree_widget.append(qtypes.String("string"))
        self.tree_widget.append(qtypes.Float("float"))
        self.tree_widget.append(qtypes.Integer("integer"))
        self.tree_widget.append(qtypes.Bool("bool"))
        self.tree_widget.append(qtypes.Enum("enum", disabled=True))
        self.tree_widget.append(qtypes.Button("button", disabled=True))

        def spawn_children(item):
            item.append(qtypes.Float("float"))
            item.append(qtypes.Bool("bool"))
            item.append(qtypes.Button("button"))

        self.tree_widget.append(qtypes.Bool("nesting"))
        spawn_children(self.tree_widget[-1])
        spawn_children(self.tree_widget[-1][0])
        spawn_children(self.tree_widget[-1][0][1])
        spawn_children(self.tree_widget[-1][0][1][2])

        self._disabled = False
        disable_button = qtypes.Button("disable")
        self.tree_widget.append(disable_button)
        disable_button._widget.clicked.connect(self._on_disable_button)

        self.setCentralWidget(self.tree_widget)

    def _on_disable_button(self):
        self._disabled = not self._disabled
        self.tree_widget[1]._widget.disabled.emit(self._disabled)
        self.tree_widget[3]._widget.disabled.emit(self._disabled)
        self.tree_widget[4]._widget.disabled.emit(self._disabled)
        self.tree_widget[5]._widget.disabled.emit(self._disabled)
        self.tree_widget[6]._widget.disabled.emit(self._disabled)



def fs():
    app = QtWidgets.QApplication(sys.argv)
    widget = MyMainWindow()
    widget.show()
    app.exec_()


if __name__ == "__main__":
    fs()
