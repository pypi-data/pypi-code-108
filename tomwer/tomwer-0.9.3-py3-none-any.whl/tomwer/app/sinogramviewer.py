#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from silx.gui import qt
import argparse
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.gui.visualization.sinogramviewer import SinogramViewer as _SinogramViewer
from tomwer.core.utils.resource import increase_max_number_file
import signal
import weakref

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


class SinogramViewer(_SinogramViewer):
    def setScan(self, scan):
        if self._scan is None or self._scan() != scan:
            self._scan = weakref.ref(scan)
            self._options.setScan(scan)


def getinputinfo():
    return "tomwer sinogram-viewer [scan_path --entry entry --line line --subsampling subsampling]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


def main(argv):
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path",
        help="path to the acquisition (folder for EDF, master file for HDF5)",
    )
    parser.add_argument(
        "--entry",
        default=None,
        help="For HDF5 acquisition you should provide an entry if several"
        "acquisitions are contained in the master file",
    )
    parser.add_argument(
        "--line",
        default=None,
        help="line to extract from radios to create the sinogram. Take the "
        "middle of projections by default",
    )
    parser.add_argument(
        "--subsampling",
        default=1,
        help="You can define a subsampling to generate the sinogram in order"
        "to speed up creation",
    )

    options = parser.parse_args(argv[1:])

    scan = ScanFactory.create_scan_object(options.scan_path, entry=options.entry)
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
    options.scan_path = options.scan_path.rstrip(os.path.sep)

    if options.subsampling < 1:
        raise ValueError("subsampling should be at least 1")

    if options.line is None:
        options.line = scan.dim_2 // 2

    if options.line < 0:
        raise ValueError("Line value should be at least 0")
    if options.line > scan.dim_2:
        raise ValueError(
            "Line value is outside frame dimension."
            "Should be at most {}".format(scan.dim_2)
        )

    widget = SinogramViewer(parent=None)
    widget.setLine(options.line)
    widget.setSubsampling(options.subsampling)
    widget.setScan(scan)
    widget.setWindowTitle("Sinogram viewer")
    widget.setWindowIcon(icons.getQIcon("tomwer"))
    splash.finish(widget)
    widget.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)
