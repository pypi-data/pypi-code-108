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


from PyQt5.QtWidgets import *

from obserware import __version__
from obserware.sources.readers.procwind.controller import (
    kill_process,
    resume_process,
    suspend_process,
    terminate_process,
)
from obserware.sources.readers.procwind.provider import (
    return_mainscreen_onetimed_statistics,
)
from obserware.sources.screens.procwind.interface import Ui_procwind


class ProcWind(QDialog, Ui_procwind):
    def __init__(self, prociden, parent=None):
        super(ProcWind, self).__init__(parent)
        self.title = "PID #%s - Obserware v%s" % (prociden, __version__)
        self.prociden = int(prociden)
        self.setupUi(self)
        self.setWindowTitle(self.title)
        self.handle_elements()

    def handle_elements(self):
        self.prepare_mainscreen_contents()

    def perform_process_killing(self):
        kill_process(self.prociden)
        self.hide()

    def perform_process_termination(self):
        terminate_process(self.prociden)
        self.hide()

    def perform_process_resuming(self):
        resume_process(self.prociden)
        self.hide()

    def perform_process_suspension(self):
        suspend_process(self.prociden)
        self.hide()

    def prepare_mainscreen_contents(self):
        retndata = return_mainscreen_onetimed_statistics(self.prociden)
        self.procname.setText(retndata["procname"])
        self.pcidtext.setText("#%d" % retndata["prociden"])
        self.cpudtext.setText("%2.1f%%" % retndata["cpu_percent"])
        self.memotext.setText("%2.1f%%" % retndata["memory_percent"])
        self.procccnm.setText(str(retndata["cpu_num"]))
        self.proctcnm.setText(str(retndata["num_threads"]))
        self.proccbnm.setText(str(retndata["username"]))
        self.proctmnm.setText(str(retndata["terminal"]))
        self.procepnm.setText(str(retndata["nice"]))
        self.procipnm.setText(str(retndata["ionice"]))
        self.procvcnm.setText(str(retndata["num_ctx_switches"]["voluntary"]))
        self.procicnm.setText(str(retndata["num_ctx_switches"]["voluntary"]))
        self.procppnm.setText(str(retndata["ppid"]))
        self.procsenm.setText(str(retndata["status"]))
        self.procstnm.setText(str(retndata["create_time"]))
        self.procmtrc.setText("Metrics acquired on %s." % str(retndata["acquired_on"]))
        self.procklbt.clicked.connect(self.perform_process_killing)
        self.proctmbt.clicked.connect(self.perform_process_termination)
        self.procrsbt.clicked.connect(self.perform_process_resuming)
        self.procspbt.clicked.connect(self.perform_process_suspension)
