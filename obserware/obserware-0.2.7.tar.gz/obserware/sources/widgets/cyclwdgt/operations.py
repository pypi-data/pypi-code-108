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
from PyQt5.QtChart import QChart, QPieSeries
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *

from obserware.sources.widgets.cyclwdgt.interface import Ui_cyclwdgt


class CyclWdgt(QWidget, Ui_cyclwdgt):
    def __init__(
        self, parent=None, cyclnumb=0, cyclperc=0, cyclcurt=0, cyclxmin=0, cyclxmax=0
    ):
        super(CyclWdgt, self).__init__(parent)
        self.setupUi(self)
        self.cpuugraf = QChart()
        self.cpuutime = QPieSeries()
        self.handle_elements(cyclnumb, cyclperc, cyclcurt, cyclxmin, cyclxmax)

    def handle_elements(self, cyclnumb, cyclperc, cyclcurt, cyclxmin, cyclxmax):
        self.cpuutime.setHoleSize(0.55)
        self.cpuugraf.setBackgroundBrush(QtGui.QColor("transparent"))
        self.cpuufrlc = self.cpuutime.append("Free", 100 - cyclperc)
        self.cpuuuslc = self.cpuutime.append("Used", cyclperc)
        self.cpuugraf.legend().hide()
        self.cpuugraf.addSeries(self.cpuutime)
        self.cpuugraf.setAnimationOptions(QChart.SeriesAnimations)
        self.cpuugraf.setContentsMargins(-35, -35, -35, -35)
        self.cyclgraf.setChart(self.cpuugraf)
        self.cyclgraf.setRenderHint(QPainter.Antialiasing)
        self.cyclnumb.setText("%d" % cyclnumb)
        self.cyclperc.setText("%d" % cyclperc)
        self.cyclcurt.setText("%s" % cyclcurt)
        self.cyclxtra.setText("<b>MIN:</b> %s, <b>MAX:</b> %s" % (cyclxmin, cyclxmax))

    def modify_attributes(self, cyclperc=0, cyclcurt=0, cyclxmin=0, cyclxmax=0):
        self.cyclperc.setText("%d" % cyclperc)
        self.cpuutime.slices()[0].setValue(100 - cyclperc)
        self.cpuutime.slices()[1].setValue(cyclperc)
        self.cyclcurt.setText("%s" % cyclcurt)
        self.cyclxtra.setText("<b>MIN:</b> %s, <b>MAX:</b> %s" % (cyclxmin, cyclxmax))
