#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from silx.gui import qt
from silx.io.utils import h5py_read_dataset
import signal
from typing import Union
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.gui.reconstruction.saaxis.saaxis import SAAxisWindow as _SAAxisWindow
from tomwer.core.process.reconstruction.axis.axis import AxisProcess, NoAxisUrl
from tomwer.core.process.reconstruction.saaxis.saaxis import SAAxisProcess
from tomwer.synctools.axis import QAxisRP
from tomwer.synctools.saaxis import QSAAxisParams
from tomwer.core.process.task import Task
from tomwer.io.utils.h5pyutils import EntryReader
from tomwer.core.process import utils as core_utils
from tomwer.core.process.reconstruction.darkref.darkrefs import (
    requires_normed_dark_and_flat,
)
from tomwer.core.utils.resource import increase_max_number_file
import logging
import time


logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


class SAAxisThread(qt.QThread):
    """
    Thread to call nabu and reconstruct one slice with several cor value
    """

    def init(self, scan, configuration, dump_roi):
        self.scan = scan
        self._configuration = configuration
        self._dump_roi = dump_roi

    def run(self) -> None:
        process = SAAxisProcess(process_id=None, inputs={"data": self.scan})
        process.set_configuration(self._configuration)
        process.dump_roi = self._dump_roi
        t0 = time.time()
        process.run()
        print("execution time is {}".format(time.time() - t0))


class SAAxisWindow(_SAAxisWindow):
    def __init__(self, parent=None, dump_roi=False):
        self._scan = None
        super().__init__(parent)
        # thread for computing cors
        self._processingThread = SAAxisThread()
        self._processingThread.finished.connect(self._threadedProcessEnded)
        self.sigStartSinogramLoad.connect(self._callbackStartLoadSinogram)
        self.sigEndSinogramLoad.connect(self._callbackEndLoadSinogram)
        self._dump_roi = dump_roi

        # hide the validate button
        self._saaxisControl._applyBut.hide()
        self.hideAutoFocusButton()

    def _launchReconstructions(self):
        if self._processingThread.isRunning():
            _logger.error(
                "a calculation is already launch. You must wait for "
                "it to end prior to launch a new one"
            )
        else:
            qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
            self._processingThread.init(
                configuration=self.getConfiguration(),
                scan=self.getScan(),
                dump_roi=self._dump_roi,
            )
            self._processingThread.start()

    def _threadedProcessEnded(self):
        saaxis_params = self._processingThread.scan.saaxis_params
        if saaxis_params is None:
            scores = None
        else:
            scores = saaxis_params.scores
        scan = self.getScan()
        assert scan is not None, "scan should have been set"
        self.setCorScores(
            scores, img_width=scan.dim_1, score_method=self.getScoreMethod()
        )
        if scan.saaxis_params.autofocus is not None:
            self.setCurrentCorValue(scan.saaxis_params.autofocus)
        self.showResults()
        qt.QApplication.restoreOverrideCursor()

    def _callbackStartLoadSinogram(self):
        print(
            "start loading sinogram for {}. Can take some time".format(self.getScan())
        )

    def _callbackEndLoadSinogram(self):
        print("sinogram loaded for {} loaded.".format(self.getScan()))

    def close(self) -> None:
        self._stopProcessingThread()
        super().close()

    def _stopProcessingThread(self):
        if self._processingThread:
            self._processingThread.terminate()
            self._processingThread.wait(500)
            self._processingThread = None

    def stop(self):
        self._stopProcessingThread()
        super().stop()

    def _computeEstimatedCor(self) -> Union[float, None]:
        scan = self.getScan()
        if scan is None:
            return
        _cor_estimation_process = AxisProcess(
            inputs={
                "axis_params": self.getQAxisRP(),
                "data": scan,
            }
        )

        _logger.info("{} - start cor estimation for".format(scan))
        qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
        try:
            _cor_estimation_process.compute(scan=scan, wait=True)
        except NoAxisUrl:
            qt.QApplication.restoreOverrideCursor()
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
            self.setEstimatedCorPosition(
                value=scan.axis_params.relative_cor_value,
            )
            qt.QApplication.restoreOverrideCursor()
            self.getAutomaticCorWindow().hide()
            return scan.axis_params.relative_cor_value

    def setDumpScoreROI(self, dump):
        self._dump_score_roi = dump


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scan_path",
        help="For EDF acquisition: provide folder path, for HDF5 / nexus "
        "provide the master file",
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
        "--read-existing",
        dest="read_existing",
        action="store_true",
        default=False,
        help="Load latest sa-delta-beta processing from *_tomwer_processes.h5 "
        "if exists",
    )
    parser.add_argument(
        "--dump-roi",
        dest="dump_roi",
        action="store_true",
        default=False,
        help="Save roi where the score is computed on the .hdf5",
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
    # define the process_index is any tomwer_processes_existing
    if options.debug:
        _logger.setLevel(logging.DEBUG)

    scan = ScanFactory.create_scan_object(
        scan_path=options.scan_path, entry=options.entry
    )
    requires_normed_dark_and_flat(scan=scan, logger_=_logger)

    window = SAAxisWindow(dump_roi=options.dump_roi)
    window.setWindowTitle("saaxis")
    window.setWindowIcon(icons.getQIcon("tomwer"))
    if scan.axis_params is None:
        scan.axis_params = QAxisRP()
    if scan.saaxis_params is None:
        scan.saaxis_params = QSAAxisParams()
    # force load of normed_flats and normed_darks
    scan.normed_flats
    scan.normed_darks
    window.setScan(scan)
    window.setDumpScoreROI(options.dump_roi)
    if options.read_existing is True:
        scores, selected = _load_latest_scores(scan)
        if scores is not None:
            window.setCorScores(scores, score_method="standard deviation")
            if selected not in (None, "-"):
                window.setCurrentCorValue(selected)

    splash.finish(window)
    window.show()
    qt.QApplication.restoreOverrideCursor()
    app.aboutToQuit.connect(window.stop)
    exit(app.exec_())


def _load_latest_scores(scan) -> tuple:
    """

    :param scan:
    :return: loaded score as (scores, selected). Scores is None or a dict.
             selected is None or a float
    """
    scores = None
    selected = None
    if scan.process_file is None:
        _logger.warning(
            "Unable to find process file. Unable to read " "existing processing"
        )
        return scores, selected

    with EntryReader(scan.process_file_url) as h5f:
        latest_saaxis_node = Task.get_most_recent_process(h5f, SAAxisProcess)
        if latest_saaxis_node and "results" in latest_saaxis_node:
            scores = core_utils.get_scores(latest_saaxis_node)
            if "center_of_rotation" in latest_saaxis_node["results"]:
                selected = h5py_read_dataset(
                    latest_saaxis_node["results"]["center_of_rotation"]
                )
        else:
            _logger.warning("no results found for {}".format(scan))
    return scores, selected


def getinputinfo():
    return "tomwer saaxis [scanDir]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


if __name__ == "__main__":
    main(sys.argv)
