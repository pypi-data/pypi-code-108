from __future__ import unicode_literals
import threading
import weakref

from appdynamics import config
from appdynamics.agent.core.logs import setup_logger
from appdynamics.priority_dict import PriorityDict


class StallMonitorService(threading.Thread):
    name = 'StallMonitorService'
    daemon = True
    agent_logger = setup_logger('appdynamics.agent')
    logger = setup_logger('appdynamics.agent.stall_monitor')
    STALLED = 'STALLED'
    ABANDONED = 'ABANDONED'

    def __init__(self, active_bts, end_transaction, time_fn):
        super(StallMonitorService, self).__init__()
        self.active_bts = active_bts
        self.end_transaction = end_transaction
        self.time_fn = time_fn
        self.monitor_lock = threading.Lock()
        self.queue_v = threading.Condition()
        self.timers = PriorityDict()
        self.timer_event = threading.Event()
        self.running = False
        self.bts = weakref.WeakValueDictionary()
        self.current_sleep = None

    def is_running(self):
        return self.running

    def start_bt_monitor(self, bt):
        with self.monitor_lock:
            if bt.bt_info_response:
                if bt.bt_info_response.currentStallThreshold:
                    expires_at = bt.timer.start_time_ms + bt.bt_info_response.currentStallThreshold
                    stall_state_at_expiry = StallMonitorService.STALLED
                else:
                    expires_at = bt.timer.start_time_ms + config.BT_MAX_DURATION_MS
                    stall_state_at_expiry = StallMonitorService.ABANDONED

                self._put(expires_at, bt.request_id, stall_state_at_expiry)
                self.bts[bt.request_id] = bt
                if self.current_sleep and expires_at < self.current_sleep:
                    self.timer_event.set()

    def end_bt_monitor(self, bt):
        with self.monitor_lock:
            try:
                self.timers.pop(bt.request_id)
                self.bts.pop(bt.request_id)
            except KeyError:
                pass

    def reset(self):
        """Remove all scheduled snapshots and put the thread to sleep.

        """
        self.timers = PriorityDict()
        self.bts.clear()

    def _put(self, expires_at, bt_id, stall_state):
        timer = (expires_at, stall_state)
        with self.queue_v:
            self.timers.additem(bt_id, timer)
            self.queue_v.notify()

    def _wait_and_start(self):
        with self.queue_v:
            while len(self.timers) == 0:
                self.queue_v.wait()
            bt_id, (expires_at, stall_state_at_expiry) = self.timers.popitem()

        now = self.time_fn()
        timeout = (expires_at - now) / 1000.0

        self.current_sleep = expires_at
        self.timer_event.wait(timeout)
        self.current_sleep = None

        bt = self.bts.get(bt_id, None)
        if bt is None or bt.completed:
            return

        if self.timer_event.is_set():
            # Sleep interrupted. Put the unexpired timer back on the heap.
            self.timer_event.clear()
            self._put(expires_at, bt_id, stall_state_at_expiry)
        else:
            bt.stall_message = self._stall_message(bt, stall_state_at_expiry)
            bt.is_stalled = True
            if stall_state_at_expiry == StallMonitorService.ABANDONED:
                del self.bts[bt.request_id]
                self.logger.info("Abandoning BT:%s (%s)" % (bt.request_id, bt.name))
                self.end_transaction(bt)
            elif stall_state_at_expiry == StallMonitorService.STALLED:
                expires_at = bt.timer.start_time_ms + (config.BT_ABANDON_THRESHOLD_MULTIPLIER *
                                                       bt.bt_info_response.currentStallThreshold)
                self._put(expires_at, bt_id, StallMonitorService.ABANDONED)

    def run(self):
        self.running = True

        while self.is_running():
            self._wait_and_start()

    def _stall_message(self, bt, stall_state):
        if stall_state == StallMonitorService.STALLED:
            threshold = bt.bt_info_response.currentStallThreshold
        else:
            if bt.bt_info_response.currentStallThreshold:
                threshold = config.BT_ABANDON_THRESHOLD_MULTIPLIER * bt.bt_info_response.currentStallThreshold
            else:
                threshold = config.BT_MAX_DURATION_MS
        message = "[%s] BT:%s (%s) Request running too long for %s ms. More than threshold %s ms." %\
                  (stall_state, bt.request_id, bt.name, bt.timer.duration_ms, threshold)
        return message
