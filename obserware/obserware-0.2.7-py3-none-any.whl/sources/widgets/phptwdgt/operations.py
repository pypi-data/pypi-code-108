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

from obserware.sources.widgets.phptwdgt.interface import Ui_phptwdgt


class PhPtWdgt(QWidget, Ui_phptwdgt):
    def __init__(
        self,
        parent=None,
        phptnumb=0,
        phptdevc="Unavailable",
        phptfutl={
            "free": "000.00XB",
            "used": "000.00XB",
            "comp": "000.00XB",
            "perc": 0.0,
        },
        phptfsys={"mtpt": "Unavailable", "fsys": "Unavailable"},
        namedist={"file": "XXX", "path": "XXX"},
    ):
        super(PhPtWdgt, self).__init__(parent)
        self.setupUi(self)
        self.handle_elements(phptnumb, phptdevc, phptfutl, phptfsys, namedist)

    def handle_elements(self, phptnumb, phptdevc, phptfutl, phptfsys, namedist):
        self.phptnumb.setText(str(phptnumb))
        self.phptdvce.setText(str(phptdevc))
        self.phptfutl.setText(
            "<b>FREE:</b> %s, <b>USED:</b> %s, <b>TOTAL:</b> %s"
            % (phptfutl["free"], phptfutl["used"], phptfutl["comp"])
        )
        self.phptpgbr.setValue(int(phptfutl["perc"]))
        self.phptfsys.setText("<b>%s</b> (%s)" % (phptfsys["mtpt"], phptfsys["fsys"]))
        self.phptmxfp.setText(
            "<b>Max filename length:</b> %s, <b>Max pathname length:</b> %s"
            % (namedist["file"], namedist["path"])
        )
