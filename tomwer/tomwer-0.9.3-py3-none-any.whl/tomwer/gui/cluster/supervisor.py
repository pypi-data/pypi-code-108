# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "14/10/2021"


from silx.gui import qt
from tomwer.core.scan.futurescan import FutureTomwerScan
from collections import OrderedDict
import functools


class FutureTomwerScanObserverWidget(qt.QWidget):
    """Widget used to observe a set of :class:`FutureTomwerScan`"""

    sigConversionPolicyChanged = qt.Signal()
    """Signal emit when the user change rule for converting finished scan"""

    sigConversionRequested = qt.Signal(object)
    """signal emit when a conversion is requested. Parameter is the future scan"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qt.QVBoxLayout())
        # filter widget
        self.filterWidget = FilterWidget(parent=self)
        self.layout().setContentsMargins(4, 4, 4, 4)
        self.layout().setSpacing(4)
        self.filterWidget.layout().setSpacing(4)
        self.layout().addWidget(self.filterWidget)
        # observation table
        self.observationTable = ObservationTable(self)
        self.layout().addWidget(self.observationTable)
        self.observationTable.setModel(
            _DatasetProcessModel(parent=self.observationTable, header=tuple())
        )
        self.observationTable.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
        self.observationTable.resizeColumnsToContents()
        self.observationTable.setSortingEnabled(True)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        # converter option
        self._commandWidget = qt.QWidget(self)
        self.layout().addWidget(self._commandWidget)
        self._commandWidget.setLayout(qt.QGridLayout())
        self._commandWidget.setContentsMargins(0, 0, 0, 0)
        spacer = qt.QWidget(self._commandWidget)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self._commandWidget.layout().addWidget(spacer, 0, 0, 1, 1)
        self._convertWhenFinished = qt.QCheckBox(
            "convert back to 'data' when finished", self
        )
        self._commandWidget.layout().addWidget(self._convertWhenFinished, 0, 1, 1, 2)
        self._convertSelectedPB = qt.QPushButton(self)
        self._convertSelectedPB.setText("convert selected")
        self._commandWidget.layout().addWidget(self._convertSelectedPB, 1, 2, 1, 1)
        self._cancelSelectedPB = qt.QPushButton(self)
        self._cancelSelectedPB.setText("cancel selected")
        style = qt.QApplication.style()
        stopIcon = style.standardIcon(qt.QStyle.SP_BrowserStop)
        self._cancelSelectedPB.setIcon(stopIcon)
        self._commandWidget.layout().addWidget(self._cancelSelectedPB, 1, 1, 1, 1)

        # set up
        self._convertWhenFinished.setChecked(True)
        h_header = self.observationTable.horizontalHeader()
        for column_index in (0, 2, 3, 4):
            h_header.setSectionResizeMode(column_index, qt.QHeaderView.Interactive)
        for column_index in (1,):
            h_header.setSectionResizeMode(column_index, qt.QHeaderView.Stretch)

        # connect signal / slot
        self.filterWidget.sigChanged.connect(self._filterUpdated)
        self._convertWhenFinished.toggled.connect(self._conversionPolicyChanged)
        self._convertSelectedPB.released.connect(self._convertSelected)
        self._cancelSelectedPB.released.connect(self._cancelSelected)

    def _convertSelected(self, *args, **kwargs):
        for cell in self.observationTable.selectionModel().selectedRows():
            future_scan = self.observationTable.model().futureScans.get(
                cell.row(), None
            )
            if future_scan is not None:
                self.sigConversionRequested.emit(future_scan)
        self.observationTable.model().endResetModel()

    def _cancelSelected(self, *args, **kwargs):
        for cell in self.observationTable.selectionModel().selectedRows():
            future_scan = self.observationTable.model().futureScans.get(
                cell.row(), None
            )
            if future_scan is not None:
                future_scan.cancel()
        self.observationTable.model().endResetModel()

    def addFutureScan(self, future_scan: FutureTomwerScan):
        self.observationTable.model().addFutureScan(future_scan)

    def removeFutureScan(self, future_scan: FutureTomwerScan):
        self.observationTable.model().removeFutureScan(future_scan)

    def _filterUpdated(self):
        self.observationTable.model().filtered_status = (
            self.filterWidget.getFilteredStatus()
        )

    def updateView(self):
        """
        Update scan view and each future scan status
        """
        self.observationTable.model().updateStatusAllFutureScans()
        self.observationTable.model().endResetModel()

    def convertWhenFinished(self):
        return self._convertWhenFinished.isChecked()

    def _conversionPolicyChanged(self, *args, **kwargs):
        self.sigConversionPolicyChanged.emit()

    def futureScans(self):
        return self.observationTable.model().futureScans

    def setConvertWhenFinished(self, convert):
        self._convertWhenFinished.setChecked(convert)


class _DatasetProcessModel(qt.QAbstractTableModel):
    sigStatusUpdated = qt.Signal(object, str)
    """Signal emit when the status of scan changes"""

    def __init__(self, parent, header, *args):
        qt.QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self.futureScans = OrderedDict()
        # key is index, value is scan
        self._filteredFutureScans = OrderedDict()
        # key is index, value is scan but only for the scan we want to display
        self._scansStatus = dict()
        # key is the future scan, value is the status of the scan
        self._filteredStatus = tuple()
        # list of status to filter
        """FutureTomwerScan with this status will be hide"""
        self._headers = {
            0: "start-time",
            1: "dataset",
            2: "status",
            3: "requester",
            4: "slurm-job",
            5: "info",
        }
        self._headersI = {v: k for k, v in self._headers.items()}
        assert len(self._headers) == len(self._headersI), "insure values are unique"

    def _computeUnfilteredFutureScans(self):
        def is_filtered(scan):
            return scan.status in self._filteredStatus

        i_row = 0
        self._filteredFutureScans = OrderedDict()

        for _, scan in self.futureScans.items():
            if not is_filtered(scan):
                self._filteredFutureScans[i_row] = scan
                i_row += 1
        return self._filteredFutureScans

    def endResetModel(self, *args, **kwargs):
        self._computeUnfilteredFutureScans()
        super().endResetModel(*args, **kwargs)

    def addFutureScan(self, future_scan):
        if not isinstance(future_scan, FutureTomwerScan):
            raise TypeError(
                f"future_scan is expected to be an instance of {FutureTomwerScan} and not {type(future_scan)}"
            )
        self.futureScans[len(self.futureScans)] = future_scan
        self._scansStatus[future_scan] = "running"
        for future in future_scan.futures:
            callback = functools.partial(
                self._updateStatus,
                future_scan=future_scan,
            )

            class CallBack:
                # we cannot create a future directly because distributed enforce
                # the callback to have a function signature with only the future
                # as single parameter.
                def __init__(self, f_partial) -> None:
                    self.f_partial = f_partial

                def process(self, fn):
                    self.f_partial()

            future.add_done_callback(CallBack(callback).process)
        self.endResetModel()

    def updateStatusAllFutureScans(self):
        for future_scan in self._scansStatus:
            self._scansStatus[future_scan] = future_scan.status

    def _updateStatus(self, future_scan):
        if future_scan is None:
            return
        status = future_scan.status
        if (
            future_scan not in self._scansStatus
            or status != self._scansStatus[future_scan]
        ):
            self._scansStatus[future_scan] = status
            self.sigStatusUpdated.emit(future_scan, status)
            self.endResetModel()

    def removeFutureScan(self, future_scan):
        for container in (self.futureScans, self._filteredFutureScans):
            futureScansI = {v: k for k, v in container.items()}
            idx = futureScansI.get(future_scan, None)
            if idx is not None:
                del container[idx]
        if future_scan in self._scansStatus:
            del self._scansStatus[future_scan]
        self.endResetModel()

    def getUnfilteredFutureScans(self):
        return self._filteredFutureScans

    @property
    def filtered_status(self):
        return self._filteredStatus

    @filtered_status.setter
    def filtered_status(self, filters):
        self._filteredStatus = filters
        self.endResetModel()

    def clear(self):
        self.futureScans = OrderedDict()
        self._filteredFutureScans = OrderedDict()
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self.getUnfilteredFutureScans())

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(self, col, orientation, role):
        if orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
            if col < len(self._headers):
                return self._headers[col]
            else:
                return None

    def data(self, index, role):
        if index.isValid() is False:
            return None

        if role not in (qt.Qt.DisplayRole, qt.Qt.ToolTipRole, qt.Qt.BackgroundRole):
            return None

        f_scan = self._filteredFutureScans[index.row()]

        def get_client_has_what_info():
            if f_scan.clients is not None:
                try:
                    return "\n".join([client.has_what() for client in f_scan.clients])
                except Exception:
                    return str()
            else:
                return str()

        if role == qt.Qt.BackgroundRole:
            if index.column() in (self._headersI["status"],):
                # color are the same as the one defined by the process manager

                if f_scan.status == "error":
                    return qt.QColor("#f52718")
                elif f_scan.status == "pending":
                    return qt.QColor("#609ab3")
                elif f_scan.status == "cancelled":
                    return qt.QColor("#fcba03")
                elif f_scan.status == "running":
                    return qt.QColor("#839684")
                elif f_scan.status == "finished":
                    return qt.QColor("#068c0c")

        elif role == qt.Qt.DisplayRole:
            col_type = self._headers[index.column()]
            if col_type == "start-time":
                return f_scan.start_time.strftime("%H:%M:%S")
            elif col_type == "dataset":
                return str(f_scan.scan.get_dataset_identifier())
            elif col_type == "requester":
                from processview.core.manager import ProcessManager

                id_ = f_scan.process_requester_id
                process = ProcessManager().get_process(id_)
                if process is not None:
                    return process.name
                else:
                    return "unknown"
            elif col_type == "status":
                return f_scan.status
            elif col_type == "slurm-job":
                infos_job = ""
                if f_scan.clients is not None:
                    for client in f_scan.clients:
                        job_ids = [str(job_id) for job_id in client.job_ids.values()]
                        infos_job += ", ".join(job_ids)
                return infos_job
            elif col_type == "info":
                return get_client_has_what_info()

        elif role == qt.Qt.ToolTipRole:
            return get_client_has_what_info()


class ObservationTable(qt.QTableView):
    def __init__(self, parent):
        qt.QTableView.__init__(self, parent)

        # QMenu
        self.menu = qt.QMenu(self)
        self._infoAction = qt.QAction("info")
        self._infoAction.triggered.connect(self._requestInfo)
        self.menu.addAction(self._infoAction)

    def _requestInfo(self, *args, **kwargs):
        raise NotImplementedError


class FilterWidget(qt.QGroupBox):
    """
    Interface to define which future to be displayed
    """

    sigChanged = qt.Signal()
    """signal emit when filter change"""

    def __init__(self, parent=None):

        super().__init__("show job with status", parent)
        self.setLayout(qt.QHBoxLayout())
        # spacer
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(spacer)

        # pending
        self._pending = qt.QCheckBox("pending", self)
        self.layout().addWidget(self._pending)
        # running
        self._running = qt.QCheckBox("running", self)
        self.layout().addWidget(self._running)
        # finished
        self._finished = qt.QCheckBox("finished", self)
        self.layout().addWidget(self._finished)
        # error
        self._error = qt.QCheckBox("error", self)
        self.layout().addWidget(self._error)
        # cancelled
        self._cancelled = qt.QCheckBox("cancelled", self)
        self.layout().addWidget(self._cancelled)

        # set up
        self._pending.setChecked(True)
        self._cancelled.setChecked(True)
        self._running.setChecked(True)
        self._finished.setChecked(True)
        self._error.setChecked(True)

        # connect signal / slot
        self._pending.toggled.connect(self._updated)
        self._cancelled.toggled.connect(self._updated)
        self._running.toggled.connect(self._updated)
        self._finished.toggled.connect(self._updated)
        self._error.toggled.connect(self._updated)

    def _updated(self):
        self.sigChanged.emit()

    def getFilteredStatus(self):
        filters = []
        cbs_filter = {
            "pending": self._pending,
            "cancelled": self._cancelled,
            "running": self._running,
            "finished": self._finished,
            "error": self._error,
        }
        for status, status_cb in cbs_filter.items():
            if not status_cb.isChecked():
                filters.append(status)
        return tuple(filters)
