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

from obserware.sources.widgets.cputwdgt.interface import Ui_cputwdgt


class CPUTWdgt(QWidget, Ui_cputwdgt):
    def __init__(
        self,
        parent=None,
        cputnumb=0,
        cputperc=0,
        secs_cputusnm=0,
        secs_cputuspr=0,
        secs_cputkrnm=0,
        secs_cputnull=0,
        secs_cputiowt=0,
        secs_cputhirq=0,
        secs_cputsirq=0,
        secs_cputvirt=0,
        secs_cputgest=0,
        secs_cputgtnc=0,
        perc_cputusnm=0,
        perc_cputuspr=0,
        perc_cputkrnm=0,
        perc_cputnull=0,
        perc_cputiowt=0,
        perc_cputhirq=0,
        perc_cputsirq=0,
        perc_cputvirt=0,
        perc_cputgest=0,
        perc_cputgtnc=0,
    ):
        super(CPUTWdgt, self).__init__(parent)
        self.setupUi(self)
        self.handle_elements(
            cputnumb,
            cputperc,
            secs_cputusnm,
            secs_cputuspr,
            secs_cputkrnm,
            secs_cputnull,
            secs_cputiowt,
            secs_cputhirq,
            secs_cputsirq,
            secs_cputvirt,
            secs_cputgest,
            secs_cputgtnc,
            perc_cputusnm,
            perc_cputuspr,
            perc_cputkrnm,
            perc_cputnull,
            perc_cputiowt,
            perc_cputhirq,
            perc_cputsirq,
            perc_cputvirt,
            perc_cputgest,
            perc_cputgtnc,
        )

    def handle_elements(
        self,
        cputnumb=0,
        cputperc=0,
        secs_cputusnm=0,
        secs_cputuspr=0,
        secs_cputkrnm=0,
        secs_cputnull=0,
        secs_cputiowt=0,
        secs_cputhirq=0,
        secs_cputsirq=0,
        secs_cputvirt=0,
        secs_cputgest=0,
        secs_cputgtnc=0,
        perc_cputusnm=0,
        perc_cputuspr=0,
        perc_cputkrnm=0,
        perc_cputnull=0,
        perc_cputiowt=0,
        perc_cputhirq=0,
        perc_cputsirq=0,
        perc_cputvirt=0,
        perc_cputgest=0,
        perc_cputgtnc=0,
    ):
        self.cputnumb.setText("%d" % cputnumb)
        self.cputperc.setText("%d%%" % cputperc)
        self.cputusnm.setText(
            "<b>Executing normal processes in user mode:</b> %s (%d%%)"
            % (secs_cputusnm, perc_cputusnm)
        )
        self.cputuspr.setText(
            "<b>Executing prioritized processes in user mode:</b> %s (%d%%)"
            % (secs_cputuspr, perc_cputuspr)
        )
        self.cputkrnm.setText(
            "<b>Executing processes in kernel mode:</b> %s (%d%%)"
            % (secs_cputkrnm, perc_cputkrnm)
        )
        self.cputnull.setText(
            "<b>Doing absolutely nothing:</b> %s (%d%%)"
            % (secs_cputnull, perc_cputnull)
        )
        self.cputiowt.setText(
            "<b>Waiting for I/O operations to complete:</b> %s (%d%%)"
            % (secs_cputiowt, perc_cputiowt)
        )
        self.cputhirq.setText(
            "<b>Servicing hardware interrupts:</b> %s (%d%%)"
            % (secs_cputhirq, perc_cputhirq)
        )
        self.cputsirq.setText(
            "<b>Servicing software interrupts:</b> %s (%d%%)"
            % (secs_cputsirq, perc_cputsirq)
        )
        self.cputvirt.setText(
            "<b>Running other OSes in a virtualized environment:</b> %s (%d%%)"
            % (secs_cputvirt, perc_cputvirt)
        )
        self.cputgest.setText(
            "<b>Running a normal virtual CPU for guest OS on Linux kernel:</b> %s (%d%%)"
            % (secs_cputgest, perc_cputgest)
        )
        self.cputgtnc.setText(
            "<b>Running a prioritized virtual CPU for guest OS on Linux kernel:</b> %s (%d%%)"
            % (secs_cputgtnc, perc_cputgtnc)
        )

    def modify_attributes(
        self,
        cputperc=0,
        secs_cputusnm=0,
        secs_cputuspr=0,
        secs_cputkrnm=0,
        secs_cputnull=0,
        secs_cputiowt=0,
        secs_cputhirq=0,
        secs_cputsirq=0,
        secs_cputvirt=0,
        secs_cputgest=0,
        secs_cputgtnc=0,
        perc_cputusnm=0,
        perc_cputuspr=0,
        perc_cputkrnm=0,
        perc_cputnull=0,
        perc_cputiowt=0,
        perc_cputhirq=0,
        perc_cputsirq=0,
        perc_cputvirt=0,
        perc_cputgest=0,
        perc_cputgtnc=0,
    ):
        self.cputperc.setText("%d%%" % cputperc)
        self.cputusnm.setText(
            "<b>Executing normal processes in user mode:</b> %s (%d%%)"
            % (secs_cputusnm, perc_cputusnm)
        )
        self.cputuspr.setText(
            "<b>Executing prioritized processes in user mode:</b> %s (%d%%)"
            % (secs_cputuspr, perc_cputuspr)
        )
        self.cputkrnm.setText(
            "<b>Executing processes in kernel mode:</b> %s (%d%%)"
            % (secs_cputkrnm, perc_cputkrnm)
        )
        self.cputnull.setText(
            "<b>Doing absolutely nothing:</b> %s (%d%%)"
            % (secs_cputnull, perc_cputnull)
        )
        self.cputiowt.setText(
            "<b>Waiting for I/O operations to complete:</b> %s (%d%%)"
            % (secs_cputiowt, perc_cputiowt)
        )
        self.cputhirq.setText(
            "<b>Servicing hardware interrupts:</b> %s (%d%%)"
            % (secs_cputhirq, perc_cputhirq)
        )
        self.cputsirq.setText(
            "<b>Servicing software interrupts:</b> %s (%d%%)"
            % (secs_cputsirq, perc_cputsirq)
        )
        self.cputvirt.setText(
            "<b>Running other OSes in a virtualized environment:</b> %s (%d%%)"
            % (secs_cputvirt, perc_cputvirt)
        )
        self.cputgest.setText(
            "<b>Running a normal virtual CPU for guest OS on Linux kernel:</b> %s (%d%%)"
            % (secs_cputgest, perc_cputgest)
        )
        self.cputgtnc.setText(
            "<b>Running a prioritized virtual CPU for guest OS on Linux kernel:</b> %s (%d%%)"
            % (secs_cputgtnc, perc_cputgtnc)
        )
