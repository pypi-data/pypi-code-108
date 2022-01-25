#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from silx.gui import qt
import signal
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.gui.visualization.dataviewer import DataViewer
from tomwer.core.utils.resource import increase_max_number_file
import logging


logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path",
        help="For EDF acquisition: provide folder path, for HDF5 / nexus "
        "provide the master file",
        default=None,
    )
    parser.add_argument(
        "entry",
        help="For Nexus files: entry in the master file",
        default=None,
        nargs="?",
    )

    options = parser.parse_args(argv[1:])

    scan = ScanFactory.create_scan_object(
        scan_path=options.scan_path, entry=options.entry
    )
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

    window = DataViewer(parent=None)
    window.setDisplayMode("radios")
    window.setWindowTitle("tomwer: scan-viewer")
    window.setWindowIcon(icons.getQIcon("tomwer"))
    window.setScan(scan)
    splash.finish(window)
    window.show()

    qt.QApplication.restoreOverrideCursor()
    app.aboutToQuit.connect(window.close)
    exit(app.exec_())


def getinputinfo():
    return "tomwer scan-viewer [file_path] [[file_entry]]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


if __name__ == "__main__":
    main(sys.argv)
