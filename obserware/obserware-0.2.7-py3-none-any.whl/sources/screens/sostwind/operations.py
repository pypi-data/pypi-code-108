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
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *

from obserware import __version__
from obserware.sources.readers import memory, time
from obserware.sources.screens.sostwind.interface import Ui_sostwind
from obserware.sources.screens.sostwind.worker import Worker

mmrysize = memory()
timevalu = time()


class SoStWind(QDialog, Ui_sostwind):
    def __init__(self, parent=None):
        super(SoStWind, self).__init__(parent)
        self.title = "Storage Counters - Obserware v%s" % __version__
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.obj = Worker()
        self.thread = QThread()
        self.handle_elements()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.thread.destroyed.connect(self.hide)

    def handle_elements(self):
        self.prepare_threaded_worker()

    def prepare_threaded_worker(self):
        self.obj.thrdstat.connect(self.place_threaded_statistics_on_screen)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.threaded_statistics_emitter)
        self.thread.start()

    def place_threaded_statistics_on_screen(self, statdict):
        # Refresh process table on the processes tab screen
        self.sostqant.setText("%d unit(s)" % statdict["provider"]["unitqant"])
        self.soctrdnm.setText(str(statdict["provider"]["diskioqt"].read_count))
        self.soctwtnm.setText(str(statdict["provider"]["diskioqt"].write_count))
        self.sobsrdnm.setText(
            mmrysize.format(statdict["provider"]["diskioqt"].read_bytes)
        )
        self.sobswtnm.setText(
            mmrysize.format(statdict["provider"]["diskioqt"].write_bytes)
        )
        self.sotmrdnm.setText(
            timevalu.format(statdict["provider"]["diskioqt"].read_time)
        )
        self.sotmwtnm.setText(
            timevalu.format(statdict["provider"]["diskioqt"].write_time)
        )
        self.somcrdnm.setText(str(statdict["provider"]["diskioqt"].read_merged_count))
        self.somcwtnm.setText(str(statdict["provider"]["diskioqt"].write_merged_count))
        self.sostbtnm.setText(
            timevalu.format(statdict["provider"]["diskioqt"].busy_time)
        )
