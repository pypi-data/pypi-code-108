#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from silx.gui import qt
import argparse
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.gui.edit.dkrfpatch import DarkRefPatchWidget
from tomwer.core.scan.scanfactory import ScanFactory
from nxtomomill.utils import add_dark_flat_nx_file
from tomwer.core.utils.resource import increase_max_number_file
import signal

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


class _DarkRefPatchDialog(qt.QDialog):
    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)
        self._scan = None
        self.setLayout(qt.QVBoxLayout())
        self._mainWidget = DarkRefPatchWidget(self)
        self.layout().addWidget(self._mainWidget)

        # buttons
        types = qt.QDialogButtonBox.Ok
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self._buttons.button(qt.QDialogButtonBox.Ok).setText("Apply")
        self.layout().addWidget(self._buttons)

        # connect signal slot
        self._buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(self._apply)

    def _apply(self):
        if self._scan is None:
            raise ValueError("Scan should be set before applying patch")
        url_sd = self._mainWidget.getStartDarkUrl()
        url_sf = self._mainWidget.getStartFlatUrl()
        url_ed = self._mainWidget.getEndDarkUrl()
        url_ef = self._mainWidget.getEndFlatUrl()
        add_dark_flat_nx_file(
            file_path=self._scan.master_file,
            entry=self._scan.entry,
            darks_start=url_sd,
            flats_start=url_sf,
            darks_end=url_ed,
            flats_end=url_ef,
        )

    def setScan(self, scan):
        self._scan = scan


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path",
        help="HDF5 - Nexus file path",
        default=None,
    )
    parser.add_argument("entry", help="NXTomo entry to load", default=None)
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )

    options = parser.parse_args(argv[1:])

    if options.debug:
        logging.root.setLevel(logging.DEBUG)

    increase_max_number_file()

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication.instance() or qt.QApplication([])
    splash = getMainSplashScreen()
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
    qt.QApplication.processEvents()

    qt.QLocale.setDefault(qt.QLocale(qt.QLocale.English))
    qt.QLocale.setDefault(qt.QLocale.c())
    signal.signal(signal.SIGINT, sigintHandler)
    sys.excepthook = qt.exceptionHandler

    timer = qt.QTimer()
    timer.start(500)
    # Application have to wake up Python interpreter, else SIGINT is not
    # catch
    timer.timeout.connect(lambda: None)

    scan = ScanFactory.create_scan_object(
        scan_path=options.scan_path, entry=options.entry
    )

    # define the process_index is any tomwer_processes_existing
    scan.set_process_index_frm_tomwer_process_file()

    if options.debug:
        _logger.setLevel(logging.DEBUG)

    window = _DarkRefPatchDialog(parent=None)
    window.setScan(scan=scan)
    window.setWindowTitle("patch dark & flat")
    window.setWindowIcon(icons.getQIcon("tomwer"))

    splash.finish(window)
    window.show()
    qt.QApplication.restoreOverrideCursor()
    app.exec_()


def getinputinfo():
    return "tomwer darkref-patch [scanDir]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


if __name__ == "__main__":
    main(sys.argv)
