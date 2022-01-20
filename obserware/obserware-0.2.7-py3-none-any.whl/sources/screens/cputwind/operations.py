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
from obserware.sources.readers.cputwind.provider import (
    return_mainscreen_onetimed_statistics,
)
from obserware.sources.screens.cputwind.interface import Ui_cputwind
from obserware.sources.screens.cputwind.worker import Worker
from obserware.sources.widgets.cputwdgt.operations import CPUTWdgt


class CPUTWind(QDialog, Ui_cputwind):
    def __init__(self, parent=None):
        super(CPUTWind, self).__init__(parent)
        self.title = "CPU Times - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.obj = Worker()
        self.thread = QThread()
        self.wdgtlist = []
        self.handle_elements()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.thread.destroyed.connect(self.hide)

    def handle_elements(self):
        self.prepare_threaded_worker()
        cpucount = return_mainscreen_onetimed_statistics()
        self.cputqant.setText("%d CPU(s)" % cpucount)
        self.cputlist.setSelectionMode(QAbstractItemView.NoSelection)
        for indx in range(cpucount):
            listitem = QListWidgetItem(self.cputlist)
            wdgtitem = CPUTWdgt(self, indx + 1)
            listitem.setSizeHint(QSize(560, 250))
            self.cputlist.setItemWidget(listitem, wdgtitem)
            self.cputlist.addItem(listitem)
            self.wdgtlist.append(wdgtitem)

    def prepare_threaded_worker(self):
        self.obj.thrdstat.connect(self.place_threaded_statistics_on_screen)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.threaded_statistics_emitter)
        self.thread.start()

    def place_threaded_statistics_on_screen(self, statdict):
        # Refresh process table on the processes tab screen
        for indx in statdict["provider"]["timedict"]:
            datadict = statdict["provider"]["timedict"][indx]
            self.wdgtlist[indx].modify_attributes(
                datadict["usage"],
                datadict["seconds"]["user"],
                datadict["seconds"]["nice"],
                datadict["seconds"]["system"],
                datadict["seconds"]["idle"],
                datadict["seconds"]["iowait"],
                datadict["seconds"]["irq"],
                datadict["seconds"]["softirq"],
                datadict["seconds"]["steal"],
                datadict["seconds"]["guest"],
                datadict["seconds"]["guest_nice"],
                datadict["percent"]["user"],
                datadict["percent"]["nice"],
                datadict["percent"]["system"],
                datadict["percent"]["idle"],
                datadict["percent"]["iowait"],
                datadict["percent"]["irq"],
                datadict["percent"]["softirq"],
                datadict["percent"]["steal"],
                datadict["percent"]["guest"],
                datadict["percent"]["guest_nice"],
            )
