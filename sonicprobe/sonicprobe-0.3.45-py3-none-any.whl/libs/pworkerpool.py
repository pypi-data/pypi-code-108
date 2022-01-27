# -*- coding: utf-8 -*-
"""pworkerpool"""

__author__  = "Adrien DELLE CAVE <adc@doowan.net>"
__license__ = """
    Copyright (C) 2017  doowan

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

import inspect
import logging
import multiprocessing
import Queue
import time


LOG = logging.getLogger('sonicprobe.pworkerpool')


class WorkerAdd(object):
    pass

class WorkerExit(object):
    pass


class WorkerProc(multiprocessing.Process):
    def __init__(self, xid, queue, shared, tasks, max_life_time, count_lock, kill_event):
        super(WorkerProc, self).__init__()
        self.daemon        = False
        self.queue         = queue
        self.shared        = shared
        self.tasks         = tasks
        self.max_life_time = max_life_time
        self.life_time     = time.time()
        self.count_lock    = count_lock
        self.kill_event    = kill_event
        self.xid           = xid

    def start(self):
        self.life_time  = time.time()
        return super(WorkerProc, self).start()

    def get_name(self, xid, name = None):
        if name:
            return "%s:%d" % (name, xid)
        else:
            return "pwpool:%d" % xid

    def expired(self):
        if self.max_life_time > 0 \
           and self.life_time > 0 \
           and (time.time() - self.life_time) >= self.max_life_time:
            return True

        return False

    def run(self):
        while True:
            try:
                task = self.tasks.get(True, 0.1)
            except IOError:
                break
            except Queue.Empty:
                continue

            if task is WorkerExit:
                break

            self.count_lock.acquire()
            self.shared['working'] += 1
            if (self.shared['working'] >= self.shared['workers']) \
               and (self.shared['workers'] < self.shared['max_workers']):
                self.count_lock.release()
                self.queue.put_nowait(WorkerAdd)
            else:
                self.count_lock.release()

            func, cb, name, args, kargs = task
            self.name = self.get_name(self.xid, name or self.shared['name'])
            try:
                if isinstance(cb, basestring) and inspect.isclass(func):
                    c = func(*args, **kargs)
                    getattr(c, cb)(ret)
                else:
                    ret = func(*args, **kargs)
                    if cb:
                        cb(ret)
            except Exception, e:
                LOG.exception("Unexpected error: %r", e)

            self.count_lock.acquire()
            self.shared['working'] -= 1
            self.count_lock.release()

            if self.expired():
                break

        self.count_lock.acquire()
        self.shared['workers'] -= 1
        self.count_lock.release()

        if not self.shared['workers']:
            self.kill_event.set()

        self.queue = None
        self.shared = None
        self.tasks = None
        self.count_lock = None
        self.kill_event = None


class PWorkerPool(multiprocessing.Process):
    def __init__(self, queue = None, max_workers = 10, life_time = None, name = None, start = True):
        super(PWorkerPool, self).__init__()
        self.tasks       = queue or multiprocessing.Queue()
        manager          = multiprocessing.Manager()
        self.shared      = manager.dict()
        self.shared['workers']     = 0
        self.shared['working']     = 0
        self.shared['max_workers'] = max_workers
        self.shared['name']        = name
        self.count_lock  = multiprocessing.RLock()
        self.kill_event  = multiprocessing.Event()
        self.life_time   = life_time
        self.name        = name
        self.queue       = multiprocessing.Queue()

        self.kill_event.set()

        if start:
            self.start()

    def count_workers(self):
        self.count_lock.acquire()
        r = self.shared['workers']
        self.count_lock.release()
        return r

    def count_working(self):
        self.count_lock.acquire()
        r = self.shared['working']
        self.count_lock.release()
        return r

    def kill(self, nb = 1):
        """
        Kill one or many workers.
        """
        self.count_lock.acquire()
        if nb > self.shared['workers']:
            nb = self.shared['workers']
        self.count_lock.release()
        for x in xrange(nb):
            self.tasks.put_nowait(WorkerExit)

    def set_max_workers(self, nb):
        """
        Set the maximum workers to create.
        """
        self.count_lock.acquire()
        self.shared['max_workers'] = nb
        if self.shared['workers'] > self.shared['max_workers']:
            self.kill(self.shared['workers'] - self.shared['max_workers'])
        self.count_lock.release()

    def get_name(self, xid, name = None):
        if name:
            return "%s:%d" % (name, xid)
        elif self.name:
            return "%s:%d" % (self.name, xid)
        else:
            return "pwpool:%d" % xid

    def add(self, nb = 1, name = None):
        """
        Create one or many workers.
        """
        for x in xrange(nb):
            self.count_lock.acquire()
            self.shared['workers'] += 1
            xid = self.shared['workers']
            self.kill_event.clear()
            self.count_lock.release()
            w   = WorkerProc(xid, self.queue, self.shared, self.tasks, self.life_time, self.count_lock, self.kill_event)
            w.name = self.get_name(xid, name)
            w.start()

    def run(self):
        while True:
            try:
                task = self.queue.get(True, 0.1)
            except IOError:
                break
            except Queue.Empty:
                continue

            if task is WorkerAdd:
                self.add()
            else:
                self.tasks.put_nowait(task)

    def put(self, target, callback = None, name = None, *args, **kargs):
        """
        Start task.
        @target: callable to run with *args and **kargs arguments.
        @callback: callable executed after target.
        """
        self.count_lock.acquire()
        if not self.shared['workers']:
            self.add(name = name)
        self.count_lock.release()
        self.queue.put_nowait((target, callback, name, args, kargs))

    def killall(self, wait = None):
        """
        Kill all active workers.
        @wait: Seconds to wait until last worker ends.
               If None it waits forever.
        """
        self.queue.close()
        self.count_lock.acquire()
        self.kill(self.shared['workers'])
        self.count_lock.release()
        self.tasks.close()
        self.terminate()
        self.kill_event.wait(wait)
