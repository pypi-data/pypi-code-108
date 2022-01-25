#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import signal
import sys
from silx.gui import qt
from tomwer.core.process.reconstruction.lamino.tofu import LaminoReconstruction
from tomwer.gui.reconstruction.lamino.tofu import TofuWindow
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.gui import icons
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.utils.resource import increase_max_number_file

_logger = logging.getLogger(__name__)
# logging.getLogger().setLevel(logging.INFO)


def getinputinfo():
    return "tomwer lamino [scanDir]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path", help="Data file to process (edf files only for now)"
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=False,
        help="Will not apply the tofu process but only display the command used"
        "to call tofu",
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
    # catched
    timer.timeout.connect(lambda: None)

    splash = getMainSplashScreen()
    options.scan_path = os.path.abspath(options.scan_path.rstrip(os.path.sep))
    scan = ScanFactory.create_scan_object(scan_path=options.scan_path)
    scan.set_process_index_frm_tomwer_process_file()
    dialog = ToFuDialog(parent=None, scan=scan)
    # dialog.tofuWidget._mainWidget._tabs._outputWidget.setOutput('')
    # dialog.tofuWidget._mainWidget._tabs._inputWidget.setWhenApplyFFC('preprocessing')
    # dialog.tofuWidget._mainWidget._tabs._inputWidget.setHalfAcquisition(True)
    dialog._setDryRun(options.dry_run)
    splash.finish(dialog)
    dialog.exec_()


class ToFuDialog(qt.QDialog):
    """Simple dialog to launch the lamino reconstruction using tofu"""

    def __init__(self, parent, scan):
        assert isinstance(scan, TomwerScanBase)
        qt.QDialog.__init__(self, parent)
        self._scan = scan
        self._dry_run = False

        self.setLayout(qt.QVBoxLayout())
        self.setWindowTitle("Lamino reconstruction using tofu")

        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self.tofuWidget = TofuWindow(parent=self)
        self.tofuWidget.loadFromScan(self._scan.path)
        self.layout().addWidget(self.tofuWidget)
        self.layout().addWidget(self._buttons)

        self._buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self._buttons.button(qt.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.setWindowIcon(icons.getQIcon("tomwer"))

    def accept(self):
        recons_param = self.tofuWidget.getParameters()
        reco_add_options = self.tofuWidget.getAdditionalRecoOptions()
        preprocess_add_options = self.tofuWidget.getAdditionalPreprocessOptions()
        delete_existing = self.tofuWidget.removeOutputDir()
        self.tofuWidget.setEnabled(False)
        qt.QApplication.processEvents()
        qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
        self._reconsProcess = LaminoReconstruction(inputs={"scan": self._scan})
        self._reconsProcess.set_configuration(
            (preprocess_add_options, reco_add_options)
        )
        self._reconsProcess.delete_existing = delete_existing
        self._reconsProcess.reconstruction_parameters = recons_param
        if self._dry_run:
            self._reconsProcess.dry_run = self._dry_run
        try:
            self._reconsProcess.run()
        except Exception as e:
            _logger.error(e)
        self.tofuWidget.setEnabled(True)
        qt.QApplication.restoreOverrideCursor()

    def _setDryRun(self, forTest):
        self._dry_run = forTest


if __name__ == "__main__":
    main(sys.argv)
