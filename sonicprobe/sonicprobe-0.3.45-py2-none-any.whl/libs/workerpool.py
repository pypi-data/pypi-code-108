# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.libs.workerpool"""

import gc
import logging
import threading
import time

from six.moves import queue as _queue, range as xrange

from sonicprobe import helpers

LOG = logging.getLogger('sonicprobe.workerpool')

DEFAULT_MAX_WORKERS   = 10
DEFAULT_EXIT_PRIORITY = -9999


class WorkerExit(object): # pylint: disable=useless-object-inheritance,too-few-public-methods
    pass


class WorkerThread(threading.Thread):
    def __init__(self, xid, pool):
        threading.Thread.__init__(self)
        self.daemon     = True
        self.pool       = pool
        self.life_time  = None
        self.nb_tasks   = None
        self.xid        = xid

    def start(self):
        self.nb_tasks   = 0
        self.life_time  = time.time()
        return threading.Thread.start(self)

    def expired(self):
        if self.pool.life_time \
           and self.pool.life_time > 0 \
           and self.life_time > 0 \
           and (time.time() - self.life_time) >= self.pool.life_time:
            LOG.debug("worker expired")
            return True

        return False

    def max_tasks_reached(self):
        if self.pool.max_tasks \
           and self.pool.max_tasks > 0 \
           and self.nb_tasks > 0 \
           and self.nb_tasks >= self.pool.max_tasks:
            LOG.debug("worker max tasks reached")
            return True

        return False

    def run(self):
        name = None

        while not self.pool.exit:
            if self.expired() or self.max_tasks_reached():
                if self.pool.auto_gc:
                    gc.collect()
                break

            if self.pool.tasks.empty():
                continue

            try:
                if not self.pool.is_qpriority:
                    task = self.pool.tasks.get_nowait()
                else:
                    qpriority, task = self.pool.tasks.get_nowait()
            except _queue.Empty:
                continue

            if self.pool.exit or isinstance(task, WorkerExit):
                break

            self.pool.count_lock.acquire()
            self.pool.working += 1
            if (not self.pool.tasks.empty() or self.pool.working >= self.pool.workers) \
               and (self.pool.workers < self.pool.max_workers):
                self.pool.count_lock.release()
                self.pool.add()
            else:
                self.pool.count_lock.release()

            func, cb, name, complete, args, kargs = task
            self.setName(self.pool.get_name(self.xid, name))

            ret = None

            try:
                self.nb_tasks += 1
                ret = func(*args, **kargs)
                if cb:
                    cb(ret)
            except Exception as e:
                LOG.exception("unexpected error: %r", e)
            except SystemExit as e:
                LOG.error("system exit: %r", e)
            finally:
                if complete:
                    complete(ret)
                del func, args, kargs

            self.pool.tasks.task_done()
            self.pool.count_lock.acquire()
            self.pool.working -= 1
            self.pool.count_lock.release()

        self.pool.count_lock.acquire()
        self.pool.workers -= 1
        if not self.pool.workers:
            self.pool.count_lock.release()
            self.pool.kill_event.set()
        else:
            self.pool.count_lock.release()

        if self.pool.exit:
            return

        self.pool.count_lock.acquire()
        if (not self.pool.tasks.empty() \
            or (self.pool.workers > 0 and self.pool.working >= self.pool.workers)) \
           and (self.pool.workers < self.pool.max_workers):
            self.pool.count_lock.release()
            self.pool.add(name = name, xid = self.xid)
        else:
            self.pool.id_list.append(self.xid)
            self.pool.count_lock.release()


class WorkerPool(object): # pylint: disable=useless-object-inheritance
    def __init__(self, queue = None, max_workers = DEFAULT_MAX_WORKERS, life_time = None, name = None, max_tasks = None, auto_gc = True):
        self.tasks        = queue or _queue.Queue()
        self.workers      = 0
        self.working      = 0
        self.max_workers  = helpers.get_nb_workers(max_workers, xmin = 1, default = DEFAULT_MAX_WORKERS)
        self.life_time    = life_time
        self.name         = name
        self.max_tasks    = max_tasks
        self.auto_gc      = auto_gc
        self.id_list      = []

        self.exit         = False
        self.kill_event   = threading.Event()
        self.count_lock   = threading.RLock()

        self.is_qpriority = isinstance(self.tasks, _queue.PriorityQueue)

        self.kill_event.set()

    def count_workers(self):
        self.count_lock.acquire()
        r = self.workers
        self.count_lock.release()
        return r

    def count_working(self):
        self.count_lock.acquire()
        r = self.working
        self.count_lock.release()
        return r

    def killable(self):
        return self.tasks.empty() and self.count_working() == 0

    def kill(self, nb = 1):
        """
        Kill one or many workers.
        """
        self.count_lock.acquire()
        if nb > self.workers:
            nb = self.workers
        self.count_lock.release()
        for x in xrange(nb): # pylint: disable=unused-variable
            if not self.is_qpriority:
                self.tasks.put(WorkerExit())
            else:
                self.tasks.put((DEFAULT_EXIT_PRIORITY, WorkerExit()))

    def set_max_workers(self, nb):
        """
        Set the maximum workers to create.
        """
        self.count_lock.acquire()
        self.max_workers = nb
        if self.workers > self.max_workers:
            self.kill(self.workers - self.max_workers)
        self.count_lock.release()

    def get_max_workers(self):
        return self.max_workers

    def get_name(self, xid, name = None):
        if name:
            return "%s:%d" % (name, xid)

        if self.name:
            return "%s:%d" % (self.name, xid)

        return "wpool:%d" % xid

    def add(self, nb = 1, name = None, xid = None):
        """
        Create one or many workers.
        """
        nb = int(nb)
        if nb < 1:
            nb = 1

        if nb > self.max_workers:
            nb = self.max_workers

        for x in xrange(nb): # pylint: disable=unused-variable
            self.count_lock.acquire()
            if self.workers >= self.max_workers:
                self.count_lock.release()
                continue
            self.workers += 1
            if xid is None:
                if self.id_list:
                    xid = self.id_list.pop(0)
                else:
                    xid = self.workers
            self.count_lock.release()
            self.kill_event.clear()
            w = WorkerThread(xid, self)
            w.setName(self.get_name(xid, name))
            w.start()

    def _run(self, target, _callback_ = None, _name_ = None, _complete_ = None, _qpriority_ = None, *args, **kwargs):
        self.count_lock.acquire()
        if not self.workers:
            self.count_lock.release()
            self.add(name = _name_)
        else:
            self.count_lock.release()

        if not self.is_qpriority:
            self.tasks.put((target, _callback_, _name_, _complete_, args, kwargs))
            return

        if _qpriority_ is None:
            _qpriority_ = time.time()
        self.tasks.put((_qpriority_, (target, _callback_, _name_, _complete_, args, kwargs)))

    def run(self, target, callback = None, name = None, complete = None, qpriority = None, *args, **kargs):
        """
        Start task.
        @target: callable to run with *args and **kargs arguments.
        @callback: callable executed after target.
        @name: thread name
        @complete: complete executed after target in finally
        @qpriority: priority for PriorityQueue
        """
        self._run(target,
                  _callback_  = callback,
                  _name_      = name,
                  _complete_  = complete,
                  _qpriority_ = qpriority,
                  *args,
                  **kargs)

    def run_args(self, target, *args, **kwargs):
        self._run(target      = target,
                  _callback_  = kwargs.pop('_callback_', None),
                  _name_      = kwargs.pop('_name_', None),
                  _complete_  = kwargs.pop('_complete_', None),
                  _qpriority_ = kwargs.pop('_qpriority_', None),
                  *args,
                  **kwargs)

    def killall(self, wait = None):
        """
        Kill all active workers.
        @wait: Seconds to wait until last worker ends.
               If None it waits forever.
        """
        self.exit = True
        with self.tasks.mutex:
            if isinstance(self.tasks.queue, list):
                self.tasks.queue[:] = []
            else:
                self.tasks.queue.clear()
        self.count_lock.acquire()
        self.kill(self.workers)
        self.count_lock.release()
        self.kill_event.wait(wait)
