import logging
import multiprocessing
import os
import sys
import threading
import time
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler


class MultiProcessingLog(logging.Handler):
    last_date = ''
    log_name = ''
    defaultFileName = ""
    dir_name = ""
    mode = ''
    maxBytes = ''
    backupCount = ''

    def __init__(self, name, mode, maxsize, rotate):
        logging.Handler.__init__(self)

        directory = "log/" + datetime.today().strftime('%Y-%m-%d')
        self.dir_name = directory
        self.log_name = name
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o777)

        filename = directory + "/" + name + "_" + datetime.today().strftime('%Y-%m-%d') + ".log"

        self.defaultFileName = name
        self._handler = RotatingFileHandler(
            filename=filename, mode=mode,
            maxBytes=maxsize, backupCount=rotate)
        self.mode = mode
        self.maxBytes = maxsize
        self.backupCount = rotate
        self.queue = multiprocessing.Queue(-1)
        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()
        self.last_date = datetime.today().strftime('%Y-%m-%d')

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                today = datetime.today().strftime('%Y-%m-%d')
                if self.last_date != today:
                    directory = "log/" + today
                    self.dir_name = directory
                    if not os.path.exists(directory):
                        os.makedirs(directory, mode=0o777)
                    filename = directory + "/" + self.log_name + "_" + today + ".log"
                    abs_path = os.path.abspath(filename)
                    if self._handler.baseFilename != abs_path:
                        self._handler.baseFilename = abs_path
                        temp_formatter = self._handler.formatter
                        self._handler = RotatingFileHandler(
                            filename=filename, mode=self.mode,
                            maxBytes=self.maxBytes, backupCount=self.backupCount)
                        self._handler.formatter = temp_formatter
                    self.last_date = today
                record = self.queue.get()
                self._handler.emit(record)
                # print('received on pid {}'.format(os.getpid()))
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except Exception as e:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):

        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        while not self.queue.empty():
            time.sleep(.1)
        self._handler.close()
        logging.Handler.close(self)

    def setFileName(self, file_name):
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            if self.last_date != today:
                directory = "log/" + today
                self.dir_name = directory
                if not os.path.exists(directory):
                    os.makedirs(directory, mode=0o777)

            filename = self.dir_name + "/" + file_name + "_" + datetime.today().strftime('%Y-%m-%d') + ".log"
            abs_path = os.path.abspath(filename)
            if self._handler.baseFilename != abs_path:
                self._handler.baseFilename = abs_path
                temp_formatter = self._handler.formatter
                self._handler = RotatingFileHandler(
                    filename=filename, mode=self.mode,
                    maxBytes=self.maxBytes, backupCount=self.backupCount)
                self._handler.formatter = temp_formatter
        except Exception as e:
            print(e)
