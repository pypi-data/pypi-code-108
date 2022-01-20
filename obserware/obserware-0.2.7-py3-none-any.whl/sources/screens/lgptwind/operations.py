"""
Obserware
Copyright (C) 2021 Akashdeep Dhar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *

from obserware import __version__
from obserware.sources.readers.lgptwind.provider import (
    return_mainscreen_onetimed_statistics,
)
from obserware.sources.screens.lgptwind.interface import Ui_lgptwind
from obserware.sources.widgets.lgptwdgt.operations import LgPtWdgt


class LgPtWind(QDialog, Ui_lgptwind):
    def __init__(self, parent=None):
        super(LgPtWind, self).__init__(parent)
        self.title = "Logical Partitions - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.handle_elements()

    def handle_elements(self):
        retndata = return_mainscreen_onetimed_statistics()
        self.lgptqant.setText("%d unit(s)" % len(retndata))
        self.lgptlist.setSelectionMode(QAbstractItemView.NoSelection)
        for indx in range(len(retndata)):
            listitem = QListWidgetItem(self.lgptlist)
            wdgtitem = LgPtWdgt(self, indx + 1)
            listitem.setSizeHint(QSize(420, 110))
            self.lgptlist.setItemWidget(listitem, wdgtitem)
            self.lgptlist.addItem(listitem)
            wdgtitem.handle_elements(
                retndata[indx]["lgptnumb"],
                retndata[indx]["lgptdevc"],
                retndata[indx]["lgptfutl"],
                retndata[indx]["lgptfsys"],
                retndata[indx]["namedist"],
            )
