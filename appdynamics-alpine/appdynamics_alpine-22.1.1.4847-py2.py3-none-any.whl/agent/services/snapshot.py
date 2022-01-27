# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Services for starting and scheduling snapshots.

"""

from __future__ import unicode_literals
import threading
import time
import weakref

from appdynamics import config
from appdynamics.lang import queue, values
from appdynamics.lib import make_uuid
from appdynamics.agent.core import correlation, snapshot
from appdynamics.agent.models.callgraph import SampleData


class SnapshotService(object):
    """A sampling profiler that runs as a separate thread.

    """
    def __init__(self, agent):
        super(SnapshotService, self).__init__()

        self.agent = agent
        self.running = False
        self.interval = config.SNAPSHOT_PROFILER_INTERVAL_MS / 1000.0
        self.logger = agent.logger

        self.scheduler = SnapshotScheduler(self)
        self.bt_lock = threading.Lock()
        self.bts = weakref.WeakValueDictionary()

        self.snapshot_event = threading.Event()

    def time(self):
        return self.agent.time()

    def is_running(self):
        return self.running

    def start(self):
        self._thread = threading.Thread(target=self._run, name='SnapshotService')
        self._thread.daemon = True
        self._thread.start()
        self.scheduler.start()

    def _run(self):
        self.running = True

        while self.is_running():
            self.snapshot_event.wait()  # Sleep until BTs are waiting for snapshots.
            self.sample()
            time.sleep(self.interval)

    def reset(self):
        """Remove all profiled BTs and put the thread to sleep.

        """
        with self.bt_lock:
            self.scheduler.reset()
            self.snapshot_event.clear()
            self.bts.clear()

    def schedule_snapshot(self, bt, slow_threshold_ms):
        """Schedule a snapshot to start after the given BT's currentSlowThreshold.

        Parameters
        ----------
        bt : appdynamics.agent.models.transactions.Transaction
            The BT to snapshot if it's slow
        slow_threshold_ms : int
            The threshold used to detect when the BT is slow, in milliseconds

        """
        self.scheduler.schedule_bt(bt, slow_threshold_ms)

    def start_snapshot(self, bt, trigger):
        """Start taking a snapshot of a BT.

        The snapshotting happens in a separate thread.

        Parameters
        ----------
        bt : appdynamics.agent.models.transactions.Transaction
            The BT to start recording a snapshot for
        trigger : {REQUIRED, CONTINUING, SLOW, ERROR}
            One of the constants from :py:mod:`appdynamics.agent.core.snapshot`
            that specify why this snapshot is being collected

        """
        if bt.snapshotting:
            return

        with self.bt_lock:
            self.logger.debug('Starting snapshot for BT %s', bt.request_id)

            start_time_ms = None

            # Just in case we somehow already started and stopped a snapshot for this BT.
            if bt.snapshot_guid is None:
                if snapshot.is_partial_snapshot(trigger, bt.started_on_time):
                    # These start whenever they were triggered.
                    start_time_ms = self.time()
                else:
                    # These always start as soon as the BT has started.
                    start_time_ms = bt.timer.start_time_ms

                bt.snapshot_start_time_ms = start_time_ms

                if bt.incoming_correlation and bt.incoming_correlation[correlation.GUID_KEY]:
                    bt.snapshot_guid = bt.incoming_correlation[correlation.GUID_KEY]
                else:
                    bt.snapshot_guid = bt.correlation_hdr_snapshot_guid or make_uuid()

                bt.snapshot_trigger = trigger
                bt.sample_data = SampleData(bt.thread_id, bt.greenlet_ref)
                bt.http_data_gatherer = self.agent.data_gatherer_registry.get_http_data_gatherer(bt.registered_id)

            bt.sample_data.sample_last_time = start_time_ms or self.time()
            self.bts[bt.request_id] = bt
            bt.snapshotting = True
            self.snapshot_event.set()

    def end_snapshot(self, bt):
        """End a snapshot for a BT.

        Parameters
        ----------
        bt : appdynamics.agent.models.transactions.Transaction

        """
        with self.bt_lock:
            self.logger.debug('Ending snapshot for BT %s', bt.request_id)

            bt.snapshotting = False
            self.bts.pop(bt.request_id, None)

            if not self.bts:
                self.logger.debug('Profiler going back to sleep')
                self.snapshot_event.clear()

    def sample(self, bt=None):
        now = self.time()

        if bt:
            bt.sample_data.take_full_stack(now, bt.active_exit_calls)
        else:
            for bt in list(values(self.bts)):  # Grab strong refs to BTs and iterate
                bt.sample_data.take_full_stack(now, bt.active_exit_calls)


class SnapshotScheduler(threading.Thread):
    """A separate thread that handles starting the profiler on slow BTs.

    Parameters
    ----------
    snapshot_svc : SnapshotService
        The snapshot service, used to start a snapshot when a BT is slow

    """
    def __init__(self, snapshot_svc):
        super(SnapshotScheduler, self).__init__()
        self.name = 'SnapshotScheduler'
        self.daemon = True

        self.snapshot_svc = snapshot_svc

        self.bts = weakref.WeakValueDictionary()
        self.timers = queue.PriorityQueue()
        self.timer_event = threading.Event()

        self.current_sleep = None

        self.running = False

    def reset(self):
        """Remove all scheduled snapshots and put the thread to sleep.

        """
        self.timers = queue.PriorityQueue()
        self.bts.clear()

    def _put(self, expires_at, bt_id):
        timer = (expires_at, bt_id)
        self.timers.put(timer)

    def schedule_bt(self, bt, slow_threshold_ms):
        """Schedule to start profiling a BT when its slow threshold is hit.

        :param appdynamics.agent.models.transactions.Transaction bt: the BT to schedule

        """
        expires_at = bt.timer.start_time_ms + slow_threshold_ms
        self._put(expires_at, bt.request_id)
        self.bts[bt.request_id] = bt

        if self.current_sleep and expires_at < self.current_sleep:
            # Interrupt our current sleep if the timer we just added would
            # expire before we wake up.
            self.timer_event.set()

    def is_running(self):
        return self.running

    def _wait_and_start(self):
        expires_at, bt_id = self.timers.get()

        now = self.snapshot_svc.time()
        timeout = (expires_at - now) / 1000.0

        self.current_sleep = expires_at
        self.timer_event.wait(timeout)
        self.current_sleep = None

        bt = self.bts.get(bt_id, None)

        if bt is None or bt.completed:
            # If the scheduled BT has completed or was GC'd, we don't need to
            # anything, even in the case that our sleep was interrupted.
            return

        if self.timer_event.is_set():
            # Sleep interrupted. Put the unexpired timer back on the heap.
            self.timer_event.clear()
            self._put(expires_at, bt_id)
        else:
            # Timeout reached. Start the snapshot_svc.
            del self.bts[bt_id]
            self.snapshot_svc.start_snapshot(bt, snapshot.SLOW)

    def run(self):
        self.running = True

        while self.is_running():
            self._wait_and_start()
