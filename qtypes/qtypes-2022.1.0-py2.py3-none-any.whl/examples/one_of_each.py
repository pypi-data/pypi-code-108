"""Example of an interface to typical daemons on the Wright Group fs system"""


import sys
import functools
import random


import qtypes
from qtpy import QtWidgets, QtGui
from qtypes._base import Base


def random_string(n):
    out = ""
    for _ in range(n):
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)  # Convert to lowercase if the flip bit is on
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        out += (chr(random_integer))
    return out


def append_inspection_widgets(root):
    # string representing value
    root.append(qtypes.String("value", disabled=True))
    def on_updated(value, item):
        item.set_value(str(value))
    root.updated.connect(functools.partial(on_updated, item=root[0]))
    on_updated(root.get(), root[0])
    # disable checkbox
    root.append(qtypes.Bool("disabled"))
    def on_updated(value, item):
        item.disabled.emit(value["value"])
    root[1].updated.connect(functools.partial(on_updated, item=root))
    # updated counter
    root.append(qtypes.Integer("updated count", disabled=True))
    def on_updated(_, item):
        item.set_value(item.get_value() + 1)
    root.updated.connect(functools.partial(on_updated, item=root[-1]))
    # edited counter
    root.append(qtypes.Integer("edited count", disabled=True))
    def on_edited(_, item):
        item.set_value(item.get_value() + 1)
    root.edited.connect(functools.partial(on_edited, item=root[-1]))


class MyMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("one of each")

        self.tree_widget = qtypes.TreeWidget()
        self.tree_widget.append(qtypes.Bool("bool"))
        self.tree_widget.append(qtypes.Button("button"))
        self.tree_widget.append(qtypes.Enum("enum", value={"value": "red", "allowed":["red", "blue", "green"]}))
        self.tree_widget.append(qtypes.Float("float"))
        self.tree_widget.append(qtypes.Integer("integer"))
        self.tree_widget.append(qtypes.String("string"))

        for child in self.tree_widget.children:
            append_inspection_widgets(child)

        self.tree_widget.append(qtypes.Button("change all programmatically"))
        self.tree_widget[-1].updated.connect(self.change_all)

        self.tree_widget.expandAll()
        self.tree_widget.resizeColumnToContents(0)
        self.setCentralWidget(self.tree_widget)

    def change_all(self, _):
        # bool
        self.tree_widget[0].set_value(not self.tree_widget[0].get_value())
        # button
        # TODO:
        # enum
        current = self.tree_widget[2].get()
        new_index = (current["allowed"].index(current["value"]) + 1) % len(current["allowed"])
        self.tree_widget[2].set_value(current["allowed"][new_index])
        # float
        self.tree_widget[3].set_value(random.uniform(-100, 100))
        # integer
        self.tree_widget[4].set_value(random.randrange(-100, 100))
        # string
        length = random.randint(5, 30)
        self.tree_widget[5].set_value(random_string(length))


def one_of_each():
    app = QtWidgets.QApplication(sys.argv)
    widget = MyMainWindow()
    widget.show()
    app.exec_()


if __name__ == "__main__":
    one_of_each()
