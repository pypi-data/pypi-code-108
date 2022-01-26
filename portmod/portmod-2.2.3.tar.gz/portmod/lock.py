# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module for handling locking

Portmod locks the system as a whole, as concurrent changes to any part of the user's
configuration may break the system.

Any major system operation should acquire the exclusive lock before starting to read from
the system configuration, guaranteeing that no other process will attempt to modify the
system while the operation is in progress.

The VDB lock prevents installed packages from being loaded while a package is being installed.
"""

import os
import tempfile
from contextlib import ContextDecorator
from typing import Dict, Optional

from fasteners import InterProcessLock, InterProcessReaderWriterLock

from portmodlib.l10n import l10n

from .globals import env


class ReentrantLock:
    def __init__(self, path: str):
        self.lock = InterProcessLock(path)
        self.level = 0

    def acquire(self) -> bool:
        if self.level == 0:
            if self.lock.acquire(timeout=0.2):
                self.level += 1
                return True
            return False
        else:
            self.level += 1
            return True

    def release(self):
        self.level -= 1
        if self.level == 0:
            self.lock.release()


class ReentrantRWLock:
    def __init__(self, path: str):
        self.lock = InterProcessReaderWriterLock(path)
        self.read_level = 0
        self.write_level = 0

    def acquire(self, write: bool = False):
        # We only initialize the bar if we can't immediately acquire the lock
        # This avoids printing the progressbar if there isn't another process running
        bar = None

        if write:
            if self.write_level == 0:
                if self.read_level:
                    self.lock.release_read_lock()
                while not self.lock.acquire_write_lock(timeout=0.2):
                    if not bar:
                        bar = _get_bar().start()
                    bar.update(status=l10n("acquiring-wirte-vdb"))

            self.write_level += 1
        else:
            if self.read_level == 0:
                while not self.lock.acquire_read_lock(timeout=0.2):
                    if not bar:
                        bar = _get_bar().start()
                    bar.update(status=l10n("acquiring-read-vdb"))

            self.read_level += 1

        if bar:
            bar.finish()

    def release(self, write: bool = False):
        if write:
            self.write_level -= 1
            self.lock.release_write_lock()
            bar = None
            if self.read_level:
                while not self.lock.acquire_read_lock(timeout=0.2):
                    if not bar:
                        bar = _get_bar().start()
                    bar.update(status=l10n("acquiring-read-vdb"))
            if bar:
                bar.finish()
        else:
            self.read_level -= 1
            if self.read_level == 0:
                self.lock.release_read_lock()


temp = tempfile.gettempdir()
LOCKS: Dict[str, ReentrantRWLock] = {}
EXCLUSIVE_LOCKS: Dict[str, ReentrantLock] = {}


def has_prefix_lock():
    if env.PREFIX_NAME in LOCKS:
        lock = LOCKS[env.PREFIX_NAME]
        return bool(lock.read_level + lock.write_level)
    return False


def has_prefix_exclusive_lock():
    if env.PREFIX_NAME in EXCLUSIVE_LOCKS:
        return bool(EXCLUSIVE_LOCKS[env.PREFIX_NAME].level)
    return False


def _clear_prefix_lock(prefix: Optional[str] = None):
    global LOCKS
    _prefix = prefix or env.PREFIX_NAME
    assert _prefix
    del LOCKS[_prefix]


def _get_bar():
    from progressbar import AnimatedMarker, ProgressBar, UnknownLength, Variable

    return ProgressBar(
        widgets=[
            Variable("status", format="{formatted_value}"),
            " ",
            AnimatedMarker(),
        ],
        max_value=UnknownLength,
    )


def get_prefix_lock(
    prefix: Optional[str] = None,
) -> ReentrantRWLock:
    global LOCKS
    _prefix = prefix or env.PREFIX_NAME
    if not _prefix:
        raise Exception("Cannot lock the system outside a prefix!")
    if _prefix in LOCKS:
        lock = LOCKS[_prefix]
    else:
        lock = LOCKS[_prefix] = ReentrantRWLock(
            os.path.join(temp, f"portmod.{env.PREFIX_NAME}.lock")
        )
    return lock


def get_prefix_exclusive_lock() -> ReentrantLock:
    global EXCLUSIVE_LOCKS
    if not env.PREFIX_NAME:
        raise Exception("Cannot lock the system outside a prefix!")
    if env.PREFIX_NAME in EXCLUSIVE_LOCKS:
        lock = EXCLUSIVE_LOCKS[env.PREFIX_NAME]
    else:
        lock = EXCLUSIVE_LOCKS[env.PREFIX_NAME] = ReentrantLock(
            os.path.join(temp, f"portmod.{env.PREFIX_NAME}.exclusive.lock")
        )
    return lock


class exclusive_lock(ContextDecorator):
    def __enter__(self):
        self.lock = get_prefix_exclusive_lock()
        self.prefix = env.PREFIX_NAME

        bar = None
        while not self.lock.acquire():
            if not bar:
                bar = _get_bar().start()
            bar.update(status=l10n("acquiring-exclusive"))
        if bar:
            bar.finish()
        return self

    def __exit__(self, *exc):
        self.lock.release()
        return False


class vdb_lock(ContextDecorator):
    def __init__(self, write: bool = False):
        self.write = write

    def __enter__(self):
        self.prefix = env.PREFIX_NAME
        lock = get_prefix_lock(self.prefix)
        if self.write:
            with exclusive_lock():
                lock.acquire(write=True)
        else:
            lock.acquire()
        return self

    def __exit__(self, *exc):
        get_prefix_lock(self.prefix).release(self.write)
        return False
