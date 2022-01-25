# coding: utf-8
###########################################################################
# Copyright (C) 2016-2019 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "28/08/2020"


from silx.gui import qt
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.process.reconstruction.nabu import nabuslices, nabuvolume
from tomwer.core.settings import get_lbsram_path, isOnLbsram
from tomwer.core.utils import isLowOnMemory
from tomwer.io.utils import format_stderr_stdout
from ..processingstack import FIFO, ProcessingThread
from processview.core.superviseprocess import SuperviseProcess
from processview.core.manager import ProcessManager, DatasetState
import gc
import logging

_logger = logging.getLogger(__name__)


class NabuSliceProcessStack(FIFO, qt.QObject):
    """Implementation of the `.AxisProcess` but having a stack for treating
    scans and making computation in threads"""

    def __init__(self, parent=None, process_id=None):
        qt.QObject.__init__(self, parent=parent)
        FIFO.__init__(self, process_id=process_id)
        self._dry_run = False

    def _process(self, scan, configuration, callback=None):
        _logger.info("Nabu slice stack is processing {}".format(str(scan)))
        ProcessManager().notify_dataset_state(
            dataset=scan,
            process=self,
            state=DatasetState.ON_GOING,
        )

        self._scan_currently_computed = scan
        assert isinstance(scan, TomwerScanBase)
        self._computationThread.finished.connect(self._end_threaded_computation)

        if isOnLbsram(scan) and isLowOnMemory(get_lbsram_path()) is True:
            # if computer is running into low memory on lbsram skip it
            mess = "low memory, skip nabu reconstruction for", scan.path
            _logger.processSkipped(mess)
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=self,
                state=DatasetState.SKIPPED,
            )
            self._end_threaded_computation()
        else:
            self._computationThread.init(scan=scan, configuration=configuration)
            self._computationThread.setDryRun(self._dry_run)
            # need to manage connect before starting it because
            self._computationThread.start()

    def _end_threaded_computation(self, callback=None):
        self._computationThread.finished.disconnect(self._end_threaded_computation)
        super()._end_threaded_computation(callback=callback)

    def _create_processing_thread(self, process_id=None) -> qt.QThread:
        return _SliceProcessingThread(process_id=process_id)

    def setDryRun(self, dry_run):
        self._dry_run = dry_run


class NabuVolumeProcessStack(NabuSliceProcessStack):
    """Implementation of the `.AxisProcess` but having a stack for treating
    scans and making computation in threads"""

    def _create_processing_thread(self, process_id=None) -> qt.QThread:
        return _VolumeProcessingThread(process_id=process_id)


class _SliceProcessingThread(ProcessingThread, SuperviseProcess):
    """
    Thread use to execute the processing of nabu reconstruction
    """

    def __init__(self, process_id=None):
        SuperviseProcess.__init__(self, process_id=process_id)
        try:
            ProcessingThread.__init__(self, process_id=process_id)
        except TypeError:
            ProcessingThread.__init__(self)
        self._scan = None
        self._future_scan = None
        self._configuration = None
        self._dry_run = False

    @property
    def future_scan(self):
        return self._future_scan

    def setDryRun(self, dry_run):
        self._dry_run = dry_run

    def init(self, scan, configuration):
        self._scan = scan
        self._configuration = configuration

    def run(self):
        self.sigComputationStarted.emit()
        mess = "Start nabu slice(s) reconstruction of {}".format(str(self._scan))
        _logger.processStarted(mess)
        ProcessManager().notify_dataset_state(
            dataset=self._scan,
            process=self,
            state=DatasetState.ON_GOING,
            details=mess,
        )

        try:
            (
                succeed,
                stdouts,
                stderrs,
                configs,
                self._future_scan,
            ) = nabuslices.run_slices_reconstruction(
                config=self._configuration,
                scan=self._scan,
                dry_run=self._dry_run,
                process_id=self.process_id,
            )
        except Exception as e:
            mess = "Fail to compute slices for {}. Reason is {}.".format(
                str(self._scan), e
            )
            _logger.processFailed(mess)
            ProcessManager().notify_dataset_state(
                dataset=self._scan,
                process=self,
                state=DatasetState.FAILED,
                details=mess,
            )
            self._future_scan = None
        else:
            index = self._scan.pop_process_index()
            if isinstance(self._scan, EDFTomoScan):
                entry = None
            else:
                entry = (
                    self._scan.entry
                )  # hotfix / FIXME: otherwise can fail to open the file to
                # register the process. Might be fix since using HDF5File
            gc.collect()
            try:
                nabuslices.NabuSlices._register_process(
                    process_file=self._scan.process_file,
                    entry=entry,
                    configuration=self._configuration,
                    results={},
                    process=nabuslices.NabuSlices,
                    process_index=index,
                    overwrite=True,
                )
            except Exception as e:
                _logger.warning(f"Fail to register NabuSlices process. Reason is {e}")

            # TODO: check output files with the tomoscan validator ?
            if not succeed:
                mess = "Slices computation for {} failed.".format(str(self._scan))
                state = DatasetState.FAILED
                _logger.processFailed(mess)
            else:
                state = DatasetState.SUCCEED
                mess = "Slices computed for {}.".format(str(self._scan))
                _logger.processSucceed(mess)
            elmts = [
                format_stderr_stdout(stderr=stderr, stdout=stdout)
                for stderr, stdout, config in zip(stderrs, stdouts, configs)
            ]
            elmts.insert(0, mess)
            details = "\n".join(elmts)

            ProcessManager().notify_dataset_state(
                dataset=self._scan,
                process=self,
                state=state,
                details=details,
            )


class _VolumeProcessingThread(_SliceProcessingThread):
    """
    Thread use to execute the processing of nabu reconstruction
    """

    def run(self):
        self.sigComputationStarted.emit()
        mess = "Start nabu volume reconstruction of {}".format(str(self._scan))
        _logger.processStarted(mess)
        ProcessManager().notify_dataset_state(
            dataset=self._scan,
            process=self,
            state=DatasetState.ON_GOING,
            details=mess,
        )
        try:
            (
                succeed,
                stdouts,
                stderrs,
                configs,
                self._future_scan,
            ) = nabuvolume.run_volume_reconstruction(
                config=self._configuration,
                scan=self._scan,
                dry_run=self._dry_run,
                process_id=self.process_id,
            )
        except Exception as e:
            self._future_scan = None
            mess = "Fail to compute volume for {}. Reason is {}".format(
                str(self._scan), e
            )
            _logger.processFailed(mess)
            ProcessManager().notify_dataset_state(
                dataset=self._scan,
                process=self,
                state=DatasetState.FAILED,
                details=mess,
            )
        else:
            index = self._scan.pop_process_index()
            if isinstance(self._scan, EDFTomoScan):
                entry = None
            else:
                entry = self._scan.entry
            gc.collect()
            try:
                nabuvolume.NabuVolume._register_process(
                    process_file=self._scan.process_file,
                    entry=entry,
                    configuration=self._configuration,
                    results={},
                    process=nabuvolume.NabuVolume,
                    process_index=index,
                    overwrite=True,
                )
            except Exception as e:
                _logger.warning(f"Fail to register NabuVolume process. Reason is {e}")
            elmts = [
                format_stderr_stdout(stderr=stderr, stdout=stdout, config=config)
                for stderr, stdout, config in zip(stderrs, stdouts, configs)
            ]

            if not succeed:
                mess = "Volume computed for {} failed.".format(str(self._scan))
                _logger.processFailed(mess)
                state = DatasetState.FAILED
            else:
                mess = "Volume computed for {}.".format(str(self._scan))
                _logger.processSucceed(mess)
                state = DatasetState.SUCCEED

            elmts.insert(0, mess)
            details = "\n".join(elmts)

            ProcessManager().notify_dataset_state(
                dataset=self._scan,
                process=self,
                state=state,
                details=details,
            )
