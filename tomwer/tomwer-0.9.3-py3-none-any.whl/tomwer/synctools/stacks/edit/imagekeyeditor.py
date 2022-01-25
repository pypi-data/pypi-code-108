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
from tomwer.core.settings import get_lbsram_path, isOnLbsram
from tomwer.core.utils import isLowOnMemory
from ..processingstack import FIFO, ProcessingThread
from tomwer.core.process.edit import imagekeyeditor
from tomoscan.esrf.hdf5scan import ImageKey
from processview.core.superviseprocess import SuperviseProcess
from processview.core.manager import ProcessManager, DatasetState
import logging

_logger = logging.getLogger(__name__)


class ImageKeyEditorProcessStack(FIFO, qt.QObject):
    """Processing stack fot image key edition"""

    def __init__(self, parent=None, process_id=None):
        qt.QObject.__init__(self, parent=parent)
        FIFO.__init__(self, process_id=process_id)
        self._dry_run = False

    def _process(self, scan, configuration, callback=None):
        _logger.info("image-key edition is processing {}".format(str(scan)))
        self._scan_currently_computed = scan
        assert isinstance(scan, TomwerScanBase)
        self._computationThread.finished.connect(self._end_threaded_computation)

        if isOnLbsram(scan) and isLowOnMemory(get_lbsram_path()) is True:
            # if computer is running into low memory on lbsram skip it
            mess = "low memory, skip image-key-edition for", scan.path
            _logger.processSkipped(mess)
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=self,
                state=DatasetState.SKIPPED,
                details=mess,
            )
            self._end_threaded_computation()
        else:
            self._computationThread.init(scan=scan, configuration=configuration)
            ProcessManager().notify_dataset_state(
                dataset=scan,
                process=self,
                state=DatasetState.ON_GOING,
            )
            # need to manage connect before starting it because
            self._computationThread.start()

    def _end_threaded_computation(self, callback=None):
        self._computationThread.finished.disconnect(self._end_threaded_computation)
        super()._end_threaded_computation(callback=callback)

    def _create_processing_thread(self, process_id=None) -> qt.QThread:
        return _ImageKeyEditorProcessingThread(process_id=process_id)


class _ImageKeyEditorProcessingThread(ProcessingThread, SuperviseProcess):
    """
    Thread use to execute image key edition
    """

    def __init__(self, process_id=None):
        try:
            ProcessingThread.__init__(self, process_id=process_id)
        except TypeError:
            ProcessingThread.__init__(self)
        self._scan = None
        self._configuration = None

    def init(self, scan, configuration):
        self._scan = scan
        self._configuration = configuration

    def run(self):
        self.sigComputationStarted.emit()
        _logger.processStarted("Start image key edition of {}".format(str(self._scan)))
        try:
            imagekeyeditor.change_image_key_control(
                config=self._configuration, scan=self._scan
            )
        except Exception as e:
            info = "Fail to edit image keys for {}. Reason is {}".format(
                str(self._scan), e
            )
            _logger.processFailed(info)
            ProcessManager().notify_dataset_state(
                dataset=self._scan,
                process=self,
                state=DatasetState.FAILED,
                details=info,
            )
        else:
            conf_to_dump = {}
            if "modifications" in self._configuration:
                for frame_index, new_frame_type in self._configuration[
                    "modifications"
                ].items():
                    conf_to_dump[str(frame_index)] = ImageKey.from_value(
                        new_frame_type
                    ).value

            index = self._scan.pop_process_index()
            try:
                imagekeyeditor.ImageKeyEditor._register_process(
                    process_file=self._scan.process_file,
                    entry=self._scan.entry,
                    configuration=conf_to_dump,
                    results={},
                    process=imagekeyeditor.ImageKeyEditor,
                    process_index=index,
                    overwrite=True,
                )
            except Exception as e:
                _logger.warning(
                    f"Fail to register ImageKeyEditor process. Reason is {e}"
                )
            info = "Image key edited for {}.".format(str(self._scan))
            _logger.processSucceed(info)
            ProcessManager().notify_dataset_state(
                dataset=self._scan,
                process=self,
                state=DatasetState.SUCCEED,
                details=info,
            )
