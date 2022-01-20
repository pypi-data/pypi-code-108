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


import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from obserware.sources.readers.sostwind.provider import (
    return_mainscreen_threaded_statistics,
)


class Worker(QObject):
    finished = pyqtSignal()
    thrdstat = pyqtSignal(dict)

    @pyqtSlot()
    def threaded_statistics_emitter(self):
        while True:
            time.sleep(1.5)
            statdict = {
                "provider": return_mainscreen_threaded_statistics(),
            }
            self.thrdstat.emit(statdict)
