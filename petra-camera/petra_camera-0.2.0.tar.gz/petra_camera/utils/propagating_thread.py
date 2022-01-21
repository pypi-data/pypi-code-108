#!/usr/bin/env python

# ----------------------------------------------------------------------
# Author:        yury.matveyev@desy.de
# ----------------------------------------------------------------------

"""
wrapper for threading.Thread, that collects error from thread and put it into Queue
"""

import threading
import sys
import traceback


class ExcThread(threading.Thread):

    # ----------------------------------------------------------------------
    def __init__(self, target, thread_name, error_bucket,  *args):
        self.ret = None
        threading.Thread.__init__(self, target=target, name=thread_name, args=args)
        self._stop_event = threading.Event()
        self.bucket = error_bucket

    # ----------------------------------------------------------------------
    def run(self):
        try:
            if hasattr(self, '_Thread__target'):
                self.ret = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
            else:
                self.ret = self._target(*self._args, **self._kwargs)

        except Exception as exp:
            print('exception caught in propagating thread:\n{}'.format(exp))
            traceback.print_tb(sys.exc_info()[2])
            self.bucket.put(sys.exc_info())

    # ----------------------------------------------------------------------
    def stop(self):
        self._stop_event.set()

    # ----------------------------------------------------------------------
    def stopped(self):
        return self._stop_event.isSet()