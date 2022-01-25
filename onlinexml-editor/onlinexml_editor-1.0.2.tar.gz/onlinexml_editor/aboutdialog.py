# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------

from datetime import datetime
import os

from PyQt5 import QtWidgets

from onlinexml_editor.gui.about_ui import Ui_AboutDialog
from onlinexml_editor.version import __version__


# ----------------------------------------------------------------------
class AboutDialog(QtWidgets.QDialog):
    """
    """
    SOURCE_DIR = "petra_camera"
    DATETIME = "%Y-%m-%d %H:%M:%S"

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)

        self._ui = Ui_AboutDialog()
        self._ui.setupUi(self)

        self._getModification()

    # ----------------------------------------------------------------------
    def _getModification(self):
        """Display last source code modification date.
        """
        mtime = 0

        for root, _, files in os.walk(self.SOURCE_DIR, topdown=True):
            for name in files:
                filename = os.path.join(root, name)
                _, ext = os.path.splitext(filename)

                if ext == ".py":
                    ftime = os.path.getmtime(filename)
                    if ftime > mtime:
                        mtime = ftime

        self._ui.lb_modified.setText("Last modification: {:s}".format(
            datetime.fromtimestamp(mtime).strftime(self.DATETIME)))
        try:
            self._ui.lb_version.setText("Version: {:s}".format(__version__))
        except:
            pass
