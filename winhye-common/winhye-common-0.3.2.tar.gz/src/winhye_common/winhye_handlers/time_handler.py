import time
import logging
import os
import multiprocessing
from logging.handlers import TimedRotatingFileHandler

lock_Rollover = multiprocessing.Lock()


class MultiProcessSafeTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False,
                 atTime=None):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        filename = self.baseFilename
        if os.path.exists(filename):
            line = open(filename, "r").readline()
            if line == '':
                t = int(time.time())
            else:
                n = line.find(',')
                line = line[1:n]
                t = int(time.mktime(time.strptime(line, '%Y-%m-%d %H:%M:%S')))
        # t = os.stat(filename)[ST_MTIME]
        else:
            t = int(time.time())
        self.rolloverAt = self.computeRollover(t)

    def emit(self, record):
        """
        Emit a record.
        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            if self.shouldRollover(record):
                if self.stream:
                    self.stream.close()
                    self.stream = None
                with lock_Rollover:
                    f = open(self.baseFilename, "r")

                    line = f.readline()
                    if line == '':
                        f.close()
                        self.doRollover()
                    else:
                        f.close()

                        n = line.find(',')
                        line = line[1:n]
                        t = int(time.mktime(time.strptime(line, '%Y-%m-%d %H:%M:%S')))

                        # last_time = int(os.stat(self.baseFilename)[ST_MTIME])#last change time
                        now = int(time.time())
                        if t >= self.rolloverAt:
                            if self.computeRollover(t) <= now:
                                self.rolloverAt = self.computeRollover(t)
                                self.doRollover()
                            else:
                                self.rolloverAt = t
                                self.stream = self._open()
                        else:
                            if self.computeRollover(t) >= now:
                                self.rolloverAt = t
                                self.stream = self._open()
                            else:
                                self.doRollover()

            logging.FileHandler.emit(self, record)
        except Exception:
            self.handleError(record)
