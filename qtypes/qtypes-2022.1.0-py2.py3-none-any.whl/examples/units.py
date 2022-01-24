"""Example of an interface to typical daemons on the Wright Group fs system"""


import sys
import functools


import qtypes
from qtpy import QtWidgets, QtGui
from qtypes._base import Base


def append_inspection_widgets(root):
    # string representing value
    root.append(qtypes.String("value", disabled=True))
    def on_updated(value, item):
        item.set_value(str(value))
    root.updated.connect(functools.partial(on_updated, item=root[0]))
    on_updated(root.get(), root[0])


class MyMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("qtypes units")

        self.tree_widget = qtypes.TreeWidget()
        self.tree_widget.append(qtypes.Float("angle", value={"value": 1.,
                                                             "units": "rad",
                                                             }))
        self.tree_widget.append(qtypes.Float("delay", value={"value": -2.,
                                                             "units": "ns",
                                                             "minimum": -4,
                                                             "maximum": 3,
                                                             }))
        self.tree_widget.append(qtypes.Float("energy", value={"value": 12500.,
                                                              "units": "wn",
                                                              "minimum": 0,
                                                              }))
        self.tree_widget.append(qtypes.Float("position", value={"value": 0.01,
                                                                "units": "in",
                                                                }))
        self.tree_widget.append(qtypes.Float("temperature", value={"value": 32.,
                                                                   "units": "deg_F",
                                                                   "minimum": -459.67,
                                                                   "maximum": 1000,
                                                                   }))

        for child in self.tree_widget.children:
            append_inspection_widgets(child)
        self.tree_widget.expandAll()
        self.tree_widget.resizeColumnToContents(0)
        self.setCentralWidget(self.tree_widget)

    def _on_disable_button(self):
        self._disabled = not self._disabled
        self.tree_widget[1]._widget.disabled.emit(self._disabled)
        self.tree_widget[3]._widget.disabled.emit(self._disabled)
        self.tree_widget[4]._widget.disabled.emit(self._disabled)
        self.tree_widget[5]._widget.disabled.emit(self._disabled)
        self.tree_widget[6]._widget.disabled.emit(self._disabled)



def units():
    app = QtWidgets.QApplication(sys.argv)
    widget = MyMainWindow()
    widget.show()
    app.exec_()


if __name__ == "__main__":
    fs()
