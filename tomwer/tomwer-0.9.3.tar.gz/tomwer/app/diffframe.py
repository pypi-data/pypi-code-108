#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from silx.gui import qt
import argparse
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.gui.visualization.diffviewer import DiffFrameViewer
from tomwer.core.utils.resource import increase_max_number_file
import signal

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def getinputinfo():
    return "tomwer nabu [scan_path]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


def main(argv):
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path", help="Data file to show (h5 file, edf files, spec files)"
    )
    parser.add_argument(
        "--entry", default=None, help="An entry should be specify for hdf5 files"
    )
    parser.add_argument("--second-scan", default=None, help="Second data files")
    parser.add_argument("--second-entry", default=None, help="Second entry")
    options = parser.parse_args(argv[1:])
    options.scan_path = options.scan_path.rstrip(os.path.sep)

    if options.second_entry is not None and options.second_scan is None:
        options.second_scan = options.scan_path

    increase_max_number_file()

    app = qt.QApplication.instance() or qt.QApplication([])

    qt.QLocale.setDefault(qt.QLocale(qt.QLocale.English))
    qt.QLocale.setDefault(qt.QLocale.c())
    signal.signal(signal.SIGINT, sigintHandler)
    sys.excepthook = qt.exceptionHandler
    timer = qt.QTimer()
    timer.start(500)
    # Application have to wake up Python interpreter, else SIGINT is not
    # catch
    timer.timeout.connect(lambda: None)

    splash = getMainSplashScreen()

    # create scan
    scan_1 = ScanFactory.create_scan_object(options.scan_path, entry=options.entry)
    if scan_1 is None:
        raise ValueError(
            "Given scan path is not recognized as a path" "containing a scan"
        )
    if options.second_scan is not None:
        scan_2 = ScanFactory.create_scan_object(
            options.second_scan, entry=options.second_entry
        )
    else:
        scan_2 = None

    # handle gui
    widget = DiffFrameViewer(parent=None)
    widget.addScan(scan_1)
    if scan_2 is not None:
        widget.addScan(scan_2)
        widget.setRightScan(scan_2)
    # for the application we run for the reconstruction to be finished
    # to give back hand to the user
    widget.setWindowTitle("Frame diff")
    widget.setWindowIcon(icons.getQIcon("tomwer"))
    splash.finish(widget)
    widget.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)
