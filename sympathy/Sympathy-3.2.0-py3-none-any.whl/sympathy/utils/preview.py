# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import threading
import ctypes
import itertools
import queue
import time
import copy

from .. platform.exceptions import sywarn
from .. platform import viewer
from .. platform.parameter_helper_gui import (
    CustomProxyParameterView, ParameterViewBase, sy_parameters)

import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets


class CancelThread(BaseException):
    pass


class CancelableThread(threading.Thread):

    def cancel(self):
        if threading.get_ident() == self.ident:
            raise CancelThread()

        tid = self.ident

        if not self.isAlive():
            sywarn('Cancel of thread that is not started')
        elif tid is not None:
            long_tid = ctypes.c_long(tid)

            gil_state = ctypes.pythonapi.PyGILState_Ensure()
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                long_tid, ctypes.py_object(CancelThread))

            if res == 0:
                sywarn('Cancel of thread that is not running')
            elif res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(long_tid, None)
                sywarn('Cancel of thread failed')

            ctypes.pythonapi.PyGILState_Release(gil_state)


class WorkerThread(CancelableThread):

    def __init__(self, target=None, args=None, **kwargs):
        self._worker_target = target
        self._worker_args = args
        super().__init__(**kwargs)

    def run(self):
        try:
            return self._worker_target(*self._worker_args)
        except CancelThread:
            pass


class MasterThread(threading.Thread):

    # Polling timeout waiting for new data and worker to finish.
    timeout = 0.2

    # Maximum time to allow job to execute, if this limit is exceeded
    # the job is cancelled.
    max_job_time = 5

    # Maximum live threads allowed (can result from delayed cancel).
    # After the maximum is reached, no new threads will be created.
    max_live_threads = 1

    def __init__(self,
                 timeout=None,
                 max_job_time=None,
                 max_live_threads=None,
                 **kwargs):

        """
        MasterThread for implementing preview functionality.

        In order for it to be useful you have to either:

        1. Create a subclass implementing _worker_function.

        See the default functions for information about what arguments to pass.

        The MasterThread itself will run as a thread, started by calling
        .start() and will in turn create a worker thread running the
        configured worker function.

        After the worker function has completed be called in the master thread.

        If timeout, max_job_time (both in float seconds) are not provided, the
        default values will be used. Likewise for max_live_threads (int).

        """

        if max_job_time is not None:
            self.max_job_time = max_job_time

        if max_live_threads is not None:
            self.max_live_threads = max_live_threads

        if timeout is not None:
            self.timeout = timeout

        assert self.timeout < 10, (
            'No point waiting longer, this value is mostly for performance')

        assert self.max_job_time < 60, (
            'No point waiting longer, this is a preview after all')

        assert self.max_live_threads < 20, (
            'A "single" preview should not require this many live threads')

        self.queue = queue.Queue()
        self.stop_event = threading.Event()

        self._worker_lock = threading.Lock()
        self._cancelled = set()
        self._job_cnt = itertools.count()
        self._threads = []
        self._job = None
        self._worker = None
        super().__init__(**kwargs)

    def _wait_for_threads(self):
        for thread in list(self._threads):
            if not thread.is_alive():
                thread.join(0)
                self._threads.remove(thread)

    def run(self):
        while not self.stop_event.is_set():
            try:
                self._job, args = self.queue.get(timeout=self.timeout)
                self._busy_function(True)
            except queue.Empty:
                pass
            else:
                self._wait_for_threads()
                while len(self._threads) > self.max_live_threads:
                    if self.stop_event.is_set():
                        return
                    self._wait_for_threads()

                with self._worker_lock:
                    self._worker = WorkerThread(
                        target=self._worker_function_ignore_exception,
                        args=args,
                        daemon=self.daemon)
                self._worker.start()
                t0 = time.time()

                while (not self.stop_event.is_set() and
                       self._worker.is_alive() and
                       self._job not in self._cancelled):
                    self._worker.join(self.timeout)
                    if time.time() - t0 > self.max_job_time:
                        self.cancel_job(self._job)
                self._worker.join(0)
                with self._worker_lock:
                    self._worker = None
                self._job = None
            if not self.stop_event.is_set():
                self._busy_function(False)

    def cancel_job(self, job):
        with self._worker_lock:
            self._cancelled.add(job)
            if self._worker and self._job == job:
                self._worker.cancel()

    def create_job(self, *args):
        job_id = next(self._job_cnt)
        self.queue.put((job_id, args))
        return job_id

    def stop(self):
        self.cancel_job(self._job)
        with self._worker_lock:
            self.stop_event.set()

    def _worker_function_ignore_exception(self, *args):
        try:
            return self._worker_function(*args)
        except Exception:
            pass

    def _worker_function(self, *args):
        """
        Perform preview calculation storing any outputs in output
        and any intermediate state in state.

        Default worker function, needs to be implemented in subclass.

        Parameters
        ----------
        args : any
            Arguments to specify the actual work to perform.
        """

        raise NotImplementedError

    def _busy_function(self, value):
        pass


class NodePreviewMasterThread(MasterThread):
    def __init__(self, output_signal, busy_signal):
        self._output_signal = output_signal
        self._busy_signal = busy_signal
        super().__init__(max_live_threads=1)

    def _worker_function(self, executor, node_context):
        executor(node_context)
        self._output_signal.emit(node_context)

    def _busy_function(self, value):
        self._busy_signal.emit(value)


class NullPreviewWidget(ParameterViewBase, QtWidgets.QLabel):
    def update_preview(self):
        pass


class PreviewWidget(QtWidgets.QWidget):
    # QtCore.Signal(NodeContext).
    preview_done = QtCore.Signal(object)
    preview_busy = QtCore.Signal(bool)

    def __init__(self, node, node_context, parameters, stable_time=1):
        super().__init__()
        # Ports are only to be used for setting up viewers, these
        # need not be stored since new port objects will result from
        # running the executor.
        self._node = node
        self._node_context = node_context
        self._parameters = parameters
        ports = node_context.output
        self._pdefs = node_context.definition['ports']['outputs']
        self._ports = [copy.deepcopy(p) for p in ports]
        self._preports = self._node._preview_ports(node_context)
        self._current_job = None
        self._busy = False
        self._waiting = False
        parameters.value_changed.add_handler(self.update_preview)

        self._viewers = []
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        views = []

        for i, (pdef, port, preport) in enumerate(zip(
                self._pdefs, ports, self._preports)):
            if preport:
                view = viewer.viewer_from_instance_factory(port)
                self._viewers.append(view)
                views.append((i, view))

        if len(views) == 1:
            layout.addWidget(views[0][1])
        elif len(views) > 1:
            tab_view = QtWidgets.QTabWidget()
            for i, view in views:
                tab_view.addTab(view, str(i))
            layout.addWidget(tab_view)

        self.setLayout(layout)

        self._thread = NodePreviewMasterThread(
            self.preview_done, self.preview_busy)
        self.preview_done.connect(self._update_preview_data)
        self._thread.start()
        self._stable_timer = QtCore.QTimer()
        self._stable_time = stable_time
        self._stable_timer.timeout.connect(self._update_preview)
        self.preview_busy.connect(self._preview_busy)

    def setVisible(self, value):
        super().setVisible(value)

        if value:
            if not self._waiting:
                self.update_preview()
        else:
            self._stable_timer.stop()

    def update_preview(self):
        self._stable_timer.setInterval(self._stable_time * 1000)
        self._stable_timer.setSingleShot(True)
        self._stable_timer.start()

    def _update_preview(self):
        if not self.isVisible():
            pass
        elif self._busy:
            self._waiting = True
        else:
            ports = [copy.deepcopy(p) for p in self._ports]
            parameters = sy_parameters(
                copy.deepcopy(self._parameters._parameter_dict))

            node_context = self._node.update_node_context(
                self._node_context, outputs=ports,
                parameters=parameters)

            self._thread.create_job(self._node.execute, node_context)
            self._waiting = False

    def _update_preview_data(self, node_context):
        ports = node_context.output
        for pdef, port, view, preport in zip(
                self._pdefs, ports, self._viewers, self._preports):
            if preport:
                view.update_data(port)

    def _preview_busy(self, value):
        self._busy = value
        if self._waiting and not self._busy:
            self._update_preview()

    def cleanup(self):
        self.preview_done.disconnect(self._update_preview_data)
        self.preview_busy.disconnect(self._preview_busy)
        self._stable_timer.timeout.disconnect(self._update_preview)
        self._stable_timer.stop()
        self._thread.stop()


class ParameterPreviewWidget(CustomProxyParameterView):

    def __init__(self, parameter_view, preview_widget, parent=None):
        super().__init__(parameter_view, parent=parent)
        self._parameter_view = parameter_view
        self._preview_widget = preview_widget

        self.setContentsMargins(0, 0, 0, 0)
        self._parameter_view.setContentsMargins(0, 0, 0, 0)
        self._preview_widget.setContentsMargins(0, 0, 0, 0)
        self._splitter = QtWidgets.QSplitter(parent=self)
        self._splitter.addWidget(self._parameter_view)

        self._preview_widget.setVisible(False)
        self._splitter.addWidget(self._preview_widget)

        parameter_view.status_changed.connect(self.status_changed)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._splitter)
        self.setLayout(layout)

    def set_preview_active(self, value):
        self._preview_widget.setVisible(value)

    def preview_active(self):
        return self._preview_widget.isVisible()

    def cleanup(self):
        super().cleanup()
        self._preview_widget.cleanup()

    def has_preview(self):
        return True


def preview_factory(node, node_context, parameters, widget):
    preview_widget = PreviewWidget(node, node_context, parameters)
    widget = ParameterPreviewWidget(widget, preview_widget)
    return widget
