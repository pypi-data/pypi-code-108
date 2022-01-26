# -*- coding: utf-8 -*-

import threading
import time


class SetInterval(threading.Thread):
    def __init__(self, callback, interval):
        """
        Helper class that run and stop the callback function after interval milliseconds.
        Realization only for Python.

        Example:

        .. code-block:: python

            def foo():
                print("interval func out")

            k = SetInterval(foo, 1000)
            k.start()
            k.stop(7000)
            print("Stop interval func")

        :param callback:  callback function to invoke
        :param interval: time in seconds after which are required to fire the callback
        """
        self.callback = callback
        self.event = threading.Event()
        self.interval = interval / 1000
        super(SetInterval, self).__init__()

    def run(self):
        while not self.event.wait(self.interval) and not self.event.is_set():
            self.callback()

    def stop(self, interval=0):
        if interval != 0:
            time.sleep(interval / 1000)
        self.event.set()
