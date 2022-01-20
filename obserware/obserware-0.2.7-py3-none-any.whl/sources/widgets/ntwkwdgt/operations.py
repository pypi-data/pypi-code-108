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
from PyQt5.QtWidgets import *

from obserware.sources.widgets.ntwkwdgt.interface import Ui_ntwkwdgt


class NtwkWdgt(QWidget, Ui_ntwkwdgt):
    def __init__(
        self,
        parent=None,
        ntwkdvce="UNAVAILABLE",
        ntwkstet="ACTIVITY",
        ntwkbrrt="0B/s",
        ntwkbtrt="0B/s",
        ntwkprrt="0Pk/s",
        ntwkptrt="0Pk/s",
        ntwkbrxc="000.00XB",
        ntwkbtxc="000.00XB",
        ntwkprxc="0",
        ntwkptxc="0",
        ntwkefrx="0",
        ntwkeftx="0",
        ntwkpdrx="0",
        ntwkpdtx="0",
    ):
        super(NtwkWdgt, self).__init__(parent)
        self.setupUi(self)
        self.handle_elements(
            ntwkdvce,
            ntwkstet,
            ntwkbrrt,
            ntwkbtrt,
            ntwkprrt,
            ntwkptrt,
            ntwkbrxc,
            ntwkbtxc,
            ntwkprxc,
            ntwkptxc,
            ntwkefrx,
            ntwkeftx,
            ntwkpdrx,
            ntwkpdtx,
        )

    def handle_elements(
        self,
        ntwkdvce,
        ntwkstet,
        ntwkbrrt,
        ntwkbtrt,
        ntwkprrt,
        ntwkptrt,
        ntwkbrxc,
        ntwkbtxc,
        ntwkprxc,
        ntwkptxc,
        ntwkefrx,
        ntwkeftx,
        ntwkpdrx,
        ntwkpdtx,
    ):
        self.ntwkdvce.setText(ntwkdvce)
        self.ntwkstet.setText("toggle-on" if ntwkstet else "toggle-off")
        self.ntwkbrrt.setText("%s (%s)" % (ntwkbrrt, ntwkprrt))
        self.ntwkbtrt.setText("%s (%s)" % (ntwkbtrt, ntwkptrt))
        self.ntwkbprx.setText(
            "<b>%s</b> received (in <b>%s</b>)" % (ntwkbrxc, ntwkprxc)
        )
        self.ntwkbptx.setText(
            "<b>%s</b> transmitted (in <b>%s</b>)" % (ntwkbtxc, ntwkptxc)
        )
        self.ntwkeprx.setText(
            "<b>%s</b> faced (<b>%s</b> dropped)" % (ntwkefrx, ntwkpdrx)
        )
        self.ntwkeptx.setText(
            "<b>%s</b> faced (<b>%s</b> dropped)" % (ntwkeftx, ntwkpdtx)
        )
