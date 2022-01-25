#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from silx.gui import qt
import signal
import functools
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.gui.reconstruction.axis import AxisWindow
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.synctools.axis import QAxisRP
from tomwer.core.process.reconstruction.axis.axis import AxisProcess, NoAxisUrl
from tomwer.core.process.reconstruction.axis.axis import AxisMode
from tomwer.core.process.reconstruction.darkref.darkrefs import (
    requires_normed_dark_and_flat,
)
from tomwer.core.utils.resource import increase_max_number_file
from silx.io.url import DataUrl
import logging


logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


class _AxisProcessGUI(AxisWindow):
    def __init__(self, scan, axis_params):
        axis_params.frame_width = scan.dim_1
        AxisWindow.__init__(self, axis_params=axis_params)
        self.hideLockButton()
        self.hideApplyButton()
        self.setScan(scan=scan)

        # connect Signal / Slot
        callback = functools.partial(self.compute, scan)
        self.sigComputationRequested.connect(callback)
        self.setWindowIcon(icons.getQIcon("tomwer"))

    def compute(self, scan, wait=True):
        mess = " ".join(
            ("start axis calculation with", scan.axis_params.axis_url_1.url.path())
        )
        _logger.info(mess)
        process = AxisProcess(
            inputs={
                "data": scan,
                "axis_params": self._axis_params,
                "wait": wait,
            }
        )
        try:
            process.run()
        except NoAxisUrl:
            msg = qt.QMessageBox(self)
            msg.setIcon(qt.QMessageBox.Warning)
            text = (
                "Unable to find url to compute the axis, please select them "
                "from the `axis input` tab"
            )
            msg.setText(text)
            msg.exec_()
            return None
        else:
            position = scan.axis_params.relative_cor_value
            assert isinstance(position, (float, type(None)))
            frm = "sinogram" if scan.axis_params.use_sinogram else "radio"
            AxisWindow.setPosition(self, frm=frm, value=position)
            return position

    def _updatePosition(self, scan):
        self._widget.setPosition(frm=None, value=scan.axis_params.relative_cor_value)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scan-path",
        help="For EDF acquisition: provide folder path, for HDF5 / nexus "
        "provide the master file",
        default=None,
    )
    parser.add_argument(
        "--use-sinogram",
        help="use the signoram from radio for computing COR. This only work"
        "with the =scan-path option",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--radio1",
        help="If you cannot provide scan-path or master file you should "
        "provide urls of the two radios to use for calculation",
        default=None,
    )
    parser.add_argument(
        "--radio2",
        help="If you cannot provide scan-path or master file you should "
        "provide urls of the two radios to use for calculation",
        default=None,
    )
    parser.add_argument(
        "--entry", help="For Nexus files: entry in the master file", default=None
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )
    parser.add_argument(
        "--mode",
        default=None,
        help="Use a specific mode. Available modes are {}" "".format(AxisMode.values()),
    )
    parser.add_argument(
        "--full-image",
        action="store_true",
        default=False,
        help="Define the mode 'full' when display shifted images from manual" " mode",
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

    mode = options.mode
    if mode is not None:
        mode = AxisMode.from_value(mode)

    try:
        scan = ScanFactory.create_scan_object(
            scan_path=options.scan_path, entry=options.entry
        )
    except ValueError as e:
        print(e)
        scan = ScanFactory.mock_scan()
        if options.radio1 is None:
            raise ValueError("At least a file or a scan path should be given")

    requires_normed_dark_and_flat(scan=scan, logger_=_logger)
    # define the process_index is any tomwer_processes_existing
    scan.set_process_index_frm_tomwer_process_file()
    if scan.axis_params is None:
        scan.axis_params = QAxisRP()
    if options.radio1 is not None:
        radio1 = DataUrl(file_path=options.radio1, scheme="fabio")
        scan.axis_params.axis_url_1 = radio1
        if options.radio2 is not None:
            radio2 = DataUrl(file_path=options.radio2, scheme="fabio")
        else:
            radio2 = None
        scan.axis_params.axis_url_2 = radio2

    if options.debug:
        _logger.setLevel(logging.DEBUG)

    axis_params = QAxisRP()
    axis_params.use_sinogram = options.use_sinogram
    if scan.dim_2 is not None:
        axis_params.sinogram_line = scan.dim_2 // 2

    window = _AxisProcessGUI(scan=scan, axis_params=axis_params)
    window.setWindowTitle("axis")
    window.setWindowIcon(icons.getQIcon("tomwer"))
    if mode is not None:
        window.setMode(mode)
    if options.full_image:
        window.manual_uses_full_image(True)

    splash.finish(window)
    window.show()
    qt.QApplication.restoreOverrideCursor()
    app.exec_()


def getinputinfo():
    return "tomwer axis [scanDir]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


if __name__ == "__main__":
    main(sys.argv)
