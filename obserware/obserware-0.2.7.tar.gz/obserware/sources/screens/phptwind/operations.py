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
from obserware.sources.readers.phptwind.provider import (
    return_mainscreen_onetimed_statistics,
)
from obserware.sources.screens.phptwind.interface import Ui_phptwind
from obserware.sources.widgets.phptwdgt.operations import PhPtWdgt


class PhPtWind(QDialog, Ui_phptwind):
    def __init__(self, parent=None):
        super(PhPtWind, self).__init__(parent)
        self.title = "Physical Partitions - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.handle_elements()

    def handle_elements(self):
        retndata = return_mainscreen_onetimed_statistics()
        self.phptqant.setText("%d unit(s)" % len(retndata))
        self.phptlist.setSelectionMode(QAbstractItemView.NoSelection)
        for indx in range(len(retndata)):
            listitem = QListWidgetItem(self.phptlist)
            wdgtitem = PhPtWdgt(self, indx + 1)
            listitem.setSizeHint(QSize(420, 110))
            self.phptlist.setItemWidget(listitem, wdgtitem)
            self.phptlist.addItem(listitem)
            wdgtitem.handle_elements(
                retndata[indx]["phptnumb"],
                retndata[indx]["phptdevc"],
                retndata[indx]["phptfutl"],
                retndata[indx]["phptfsys"],
                retndata[indx]["namedist"],
            )
