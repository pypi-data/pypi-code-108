#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from silx.gui import qt
import argparse
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.gui.reconstruction.nabu.slices import NabuDialog
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.process.reconstruction.nabu.nabuslices import run_slices_reconstruction
from tomwer.gui.visualization.dataviewer import DataViewer as _DataViewer
from tomwer.core.utils.resource import increase_max_number_file
import signal

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def getinputinfo():
    return "tomwer nabu [scan_path]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


class DataViewer(_DataViewer):
    """The data viewer with an update when F5 is press"""

    closed = qt.Signal()
    """signal emitted when the widget is closing"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(qt.Qt.WA_DeleteOnClose)

    def keyPressEvent(self, event):
        if event.key() is qt.Qt.Key_F5:
            self._updateDisplay()

    def event(self, event) -> bool:
        if event.type() == qt.QEvent.DeferredDelete:
            self.cleanBeforeQuit()
            self.closed.emit()
        return super().event(event)


class NabuProcessingThread(qt.QThread):
    def init(self, scan, config, dry_run=False):
        self._scan = scan
        self._config = config
        self._dry_run = dry_run

    def run(self):
        run_slices_reconstruction(
            scan=self._scan, config=self._config, dry_run=self._dry_run
        )


class _CORWidget(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())
        self.layout().addWidget(qt.QLabel("center of rotation", self))
        self._corCN = qt.QCheckBox("auto", self)
        self.layout().addWidget(self._corCN)
        self._corQLE = qt.QLineEdit("0", self)
        self._corQLE.setValidator(qt.QDoubleValidator(self))
        self.layout().addWidget(self._corQLE)
        self._corQLE.setToolTip("Value should be in -width/2, width/2")

        # set up
        self._corCN.setChecked(True)
        self._corQLE.setEnabled(False)

        # connect signal / slot
        self._corCN.toggled.connect(self._corQLE.setDisabled)

    def getCOR(self):
        if self._corCN.isChecked():
            return "auto"
        else:
            return float(self._corQLE.text())


class NabuWindow(NabuDialog):
    def __init__(self, parent=None):
        NabuDialog.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        self.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.__scan = None
        self.__processingThread = NabuProcessingThread()
        self._dry_run = False

        # add center of rotation widget
        self._corWidget = _CORWidget(parent=self)
        rw = self._widget._mainWidget._configuration._reconstructionWidget
        rw.layout().addWidget(self._corWidget, 99, 0, 1, 2)

        self._dataViewer = None
        self.setModal(False)

        # add view button
        self._showPB = qt.QPushButton("show scan", self)
        self._buttons.addButton(self._showPB, qt.QDialogButtonBox.ActionRole)

        # connect signal / slot
        self._computePB.released.connect(self._requireComputation)
        self._showPB.released.connect(self._showScan)

        # export API
        self.getCOR = self._corWidget.getCOR

    def _showScan(self):
        self._getDataViewer().setScan(self.__scan)
        self._getDataViewer().show()
        self._getDataViewer().raise_()

    def _getDataViewer(self):
        if self._dataViewer is None:
            self._dataViewer = DataViewer(parent=None)
            self._dataViewer.closed.connect(self._viewerDeleted)

        return self._dataViewer

    def _viewerDeleted(self):
        self._dataViewer = None

    def setScan(self, scan):
        self.__scan = scan
        NabuDialog.setScan(self, scan)

    def getScan(self):
        return self.__scan

    def getConfiguration(self):
        config = super().getConfiguration()
        cor = self.getCOR()
        if cor != "auto":
            # move the cor value to the nabu reference
            cor = cor + self.__scan.dim_1 // 2
        config["reconstruction"]["rotation_axis_position"] = str(cor)
        return config

    def _requireComputation(self, *arg, **kwargs):
        _logger.info("start computation")
        scan = self.getScan()
        if scan is not None:
            qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
            self._launchComputation(scan=scan, config=self.getConfiguration())

    def _computationEnded(self):
        _logger.info("end computation")
        qt.QApplication.restoreOverrideCursor()
        if self._dataViewer is not None:
            self._dataViewer.setScan(self.__scan)

    def getProcessingThread(self):
        return self.__processingThread

    def _launchComputation(self, scan, config):
        # update the processing thread
        thread = self.getProcessingThread()
        thread.init(scan=scan, config=config, dry_run=self._dry_run)
        thread.finished.connect(self._computationEnded)

        # start processing
        thread.start(priority=qt.QThread.LowPriority)

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    def close(self):
        super().close()
        if self._dataViewer is not None:
            self._dataViewer.close()
            self._dataViewer = None

    def _aboutToQuit(self):
        if self._dataViewer is not None:
            self._dataViewer.cleanBeforeQuit()


def main(argv):
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path", help="Data file to show (h5 file, edf files, spec files)"
    )
    parser.add_argument(
        "--entry", default=None, help="An entry should be specify for hdf5 files"
    )
    parser.add_argument(
        "--output-dir", help="output directory of the reconstruction(s)"
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
        help="Only create the .nabu file and print the configuration used",
    )
    options = parser.parse_args(argv[1:])

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
    options.scan_path = options.scan_path.rstrip(os.path.sep)
    scan = ScanFactory.create_scan_object(options.scan_path, entry=options.entry)
    widget = NabuWindow(parent=None)
    widget.setScan(scan)
    scan.set_process_index_frm_tomwer_process_file()
    if options.output_dir is not None:
        widget.setOutputDir(options.output_dir)
    # for the application we run for the reconstruction to be finished
    # to give back hand to the user
    widget.set_dry_run(options.dry_run)
    widget.setWindowTitle("Nabu reconstruction")
    widget.setWindowIcon(icons.getQIcon("tomwer"))
    splash.finish(widget)
    widget.show()
    qt.QApplication.instance().aboutToQuit.connect(widget._aboutToQuit)

    app.exec_()


if __name__ == "__main__":
    main(sys.argv)
