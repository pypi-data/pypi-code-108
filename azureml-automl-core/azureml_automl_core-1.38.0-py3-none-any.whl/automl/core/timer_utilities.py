# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Timer utility classes."""

from threading import Timer


class TimerCallback(object):
    """
    Class for timer callback.

    Ensures the callback is called continuously w/interval until stop is called.
    """

    def __init__(self, interval=1, callback=None, *args, **kwargs):
        """
        Initialize timer callback.

        :param interval: callback interval
        :param callback:  function to be called
        :param args: args
        :param kwargs: kwargs
        """
        self._timer = Timer(interval, self._run)
        self._timer.daemon = True
        self.interval = interval
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.stop_requested = False

    def _run(self):
        """
        Invoke the callback.

        :return: None
        """
        try:
            if self.callback is not None:
                self.callback(*self.args, **self.kwargs)
        except Exception:
            # aml logger may not be available at this time.
            pass
        finally:
            if not self.stop_requested:
                self.is_running = False
                self.start()

    def start(self):
        """
        Start the timer for callback.

        :return:
        """
        if not self.is_running:
            self.is_running = True
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
        else:
            raise RuntimeError('Timer is already running.')

    def stop(self):
        """
        Stop the timer.

        :return:
        """
        if self.is_running:
            self.stop_requested = True
            self.is_running = False
            self._timer.cancel()
        else:
            raise RuntimeError('Timer was not running.')
