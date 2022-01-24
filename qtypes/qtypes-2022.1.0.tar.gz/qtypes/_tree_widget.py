__all__ = ["TreeWidget"]


import sys
import pathlib

from qtpy import QtWidgets, QtGui, QtCore

from ._base import Base
from ._styles import styles


__here__ = pathlib.Path(__file__).parent


class TreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, *, parent=None, width=250):
        super().__init__(parent=parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["", ""])
        sheets = list(styles["tomorrow-night"].values())
        self.setStyleSheet("".join(sheets))
        self.setColumnWidth(width//2, width//2)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.children = []

    def __getitem__(self, index):
        if index < 0:
            index = self.topLevelItemCount() + index
        return self.topLevelItem(index)

    def append(self, item):
        self.addTopLevelItem(item)
        if isinstance(item, Base):
            widget = item._widget
            widget.setParent(self)
            self.setItemWidget(item, 1, widget)
            self.children.append(item)
