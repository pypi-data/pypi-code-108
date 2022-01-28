#!/usr/bin/env python3

import logging
import queue
import sqlite3
import threading
import traceback
import typing
from pathlib import Path


class StatTracker:
    def __init__(self, database: Path, shutdown_event: threading.Event = threading.Event()):
        """
        Stat tracker
        :param database: path to db file
        :param shutdown_event: Event to remotely trigger shutdown. Leave unset to generate one. Will be set on del.
        :param disable: Don't actually do anything, discard input
        """
        self._shutdown = shutdown_event

        self._queue = queue.Queue()
        self._closed = threading.Event()

        self._writer = threading.Thread(target=self._writer_func, name='stat_writer', args=(database,))
        self._writer.start()

    def _writer_func(self, db_path):
        db = sqlite3.connect(str(db_path))
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS stats (source text, sender text, func_name text, timestamp real, message text);')
        while not self._shutdown.is_set():
            self._shutdown.wait(300)  # flush every 5 minutes
            if not self._queue.empty():
                logging.info('Saving stats')
                entry = None
                try:
                    with db:
                        while not self._queue.empty():
                            entry = self._queue.get()
                            db.execute('INSERT INTO stats VALUES (?, ?, ?, ?, ?)', entry)
                except Exception as err:
                    logging.error(f'{err} during stat database flush for entry {entry}')
                    logging.error(traceback.format_exc())
        db.close()
        self._closed.set()

    def submit(self, source: str, sender: str, func_name: str, timestamp: int, message: str):
        # Hope that blocking record doesn't come back to bite me
        self._queue.put((source, sender, func_name, timestamp, message))

    def wait(self):
        self._closed.wait()

    def __del__(self):
        if self._writer is not None:
            self._shutdown.set()
            self._writer.join()
            self._writer = None


class StubTracker(StatTracker):
    def __init__(self, *args, **kwargs):
        pass

    def submit(self, *args, **kwargs):
        pass

    def wait(self):
        pass

    def __del__(self):
        pass
