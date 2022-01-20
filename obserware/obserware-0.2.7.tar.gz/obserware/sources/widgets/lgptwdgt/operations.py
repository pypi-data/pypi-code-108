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

from obserware.sources.widgets.lgptwdgt.interface import Ui_lgptwdgt


class LgPtWdgt(QWidget, Ui_lgptwdgt):
    def __init__(
        self,
        parent=None,
        lgptnumb=0,
        lgptdevc="Unavailable",
        lgptfutl={
            "free": "000.00XB",
            "used": "000.00XB",
            "comp": "000.00XB",
            "perc": 0.0,
        },
        lgptfsys={"mtpt": "Unavailable", "fsys": "Unavailable"},
        namedist={"file": "XXX", "path": "XXX"},
    ):
        super(LgPtWdgt, self).__init__(parent)
        self.setupUi(self)
        self.handle_elements(lgptnumb, lgptdevc, lgptfutl, lgptfsys, namedist)

    def handle_elements(self, lgptnumb, lgptdevc, lgptfutl, lgptfsys, namedist):
        self.lgptnumb.setText(str(lgptnumb))
        self.lgptdvce.setText(str(lgptdevc))
        self.lgptfutl.setText(
            "<b>FREE:</b> %s, <b>USED:</b> %s, <b>TOTAL:</b> %s"
            % (lgptfutl["free"], lgptfutl["used"], lgptfutl["comp"])
        )
        self.lgptpgbr.setValue(int(lgptfutl["perc"]))
        self.lgptfsys.setText("<b>%s</b> (%s)" % (lgptfsys["mtpt"], lgptfsys["fsys"]))
        self.lgptmxfp.setText(
            "<b>Max filename length:</b> %s, <b>Max pathname length:</b> %s"
            % (namedist["file"], namedist["path"])
        )
