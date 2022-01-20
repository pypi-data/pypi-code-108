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


from PyQt5 import QtGui
from PyQt5.QtCore import QSize, QThread
from PyQt5.QtWidgets import *

from obserware import __version__
from obserware.sources.readers.cyclwind.provider import (
    return_mainscreen_onetimed_statistics,
)
from obserware.sources.screens.cyclwind.interface import Ui_cyclwind
from obserware.sources.screens.cyclwind.worker import Worker
from obserware.sources.widgets.cyclwdgt.operations import CyclWdgt


class CyclWind(QDialog, Ui_cyclwind):
    def __init__(self, parent=None):
        super(CyclWind, self).__init__(parent)
        self.title = "CPU Cycles - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.obj = Worker()
        self.thread = QThread()
        self.wdgtlist = []
        self.cputwind = parent.cputwind
        self.handle_elements()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.thread.destroyed.connect(self.hide)

    def handle_elements(self):
        self.prepare_threaded_worker()
        self.cycsecbt.clicked.connect(self.cputwind.exec)
        cpucount = return_mainscreen_onetimed_statistics()
        self.cyclqant.setText("%d CPU(s)" % cpucount)
        self.cycllist.setSelectionMode(QAbstractItemView.NoSelection)
        for indx in range(cpucount):
            listitem = QListWidgetItem(self.cycllist)
            wdgtitem = CyclWdgt(self, indx + 1)
            listitem.setSizeHint(QSize(350, 50))
            self.cycllist.setItemWidget(listitem, wdgtitem)
            self.cycllist.addItem(listitem)
            self.wdgtlist.append(wdgtitem)

    def prepare_threaded_worker(self):
        self.obj.thrdstat.connect(self.place_threaded_statistics_on_screen)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.threaded_statistics_emitter)
        self.thread.start()

    def place_threaded_statistics_on_screen(self, statdict):
        # Refresh process table on the processes tab screen
        for indx in statdict["provider"]:
            datadict = statdict["provider"][indx]
            self.wdgtlist[indx].modify_attributes(
                datadict["percent"],
                datadict["frequency"]["cur"],
                datadict["frequency"]["min"],
                datadict["frequency"]["max"],
            )
