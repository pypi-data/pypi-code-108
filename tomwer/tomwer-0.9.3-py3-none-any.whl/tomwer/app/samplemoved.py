#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from silx.gui import qt
import argparse
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.gui import icons
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.gui.samplemoved import SampleMovedWidget
from tomwer.core.utils.resource import increase_max_number_file
import os
import signal

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def getinputinfo():
    return "tomwer samplemoved [scanDir]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path", help="Data file to show (h5 file, edf files, spec files)"
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )
    parser.add_argument(
        "--entry",
        help="For Nexus files: entry in the master file",
        default=None,
    )
    options = parser.parse_args(argv[1:])

    increase_max_number_file()

    global app  # QApplication must be global to avoid seg fault on quit
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
    widget = SampleMovedWidget()
    widget.setWindowIcon(icons.getQIcon("tomwer"))
    options.scan_path = options.scan_path.rstrip(os.path.sep)

    scan = ScanFactory.create_scan_object(options.scan_path, options.entry)
    rawSlices = scan.get_proj_angle_url()
    widget.setImages(rawSlices)
    # TODO: set back the flat field correction
    splash.finish(widget)
    widget.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)
