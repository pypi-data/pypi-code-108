# Copyright (C) 2018-2022  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


import io
import os
import shutil
import signal
import time
import traceback
from typing import Callable

from billiard import Process, Queue  # type: ignore
import psutil


def clean_dangling_folders(dirpath: str, pattern_check: str, log=None) -> None:
    """Clean up potential dangling temporary working folder rooted at `dirpath`. Those
       folders must match a dedicated pattern and not belonging to a live pid.

    Args:
        dirpath: Path to check for dangling files
        pattern_check: A dedicated pattern to check on first level directory (e.g
            `swh.loader.mercurial.`, `swh.loader.svn.`)
        log (Logger): Optional logger

    """
    if not os.path.exists(dirpath):
        return
    for filename in os.listdir(dirpath):
        path_to_cleanup = os.path.join(dirpath, filename)
        try:
            # pattern: `swh.loader.{loader-type}-pid.{noise}`
            if (
                pattern_check not in filename or "-" not in filename
            ):  # silently ignore unknown patterns
                continue
            _, pid_ = filename.split("-")
            pid = int(pid_.split(".")[0])
            if psutil.pid_exists(pid):
                if log:
                    log.debug("PID %s is live, skipping", pid)
                continue
            # could be removed concurrently, so check before removal
            if os.path.exists(path_to_cleanup):
                shutil.rmtree(path_to_cleanup)
        except Exception as e:
            if log:
                log.warn("Fail to clean dangling path %s: %s", path_to_cleanup, e)


class CloneTimeout(Exception):
    pass


class CloneFailure(Exception):
    pass


def _clone_task(clone_func: Callable[[], None], errors: Queue) -> None:
    try:
        clone_func()
    except Exception as e:
        exc_buffer = io.StringIO()
        traceback.print_exc(file=exc_buffer)
        errors.put_nowait(exc_buffer.getvalue())
        raise e


def clone_with_timeout(
    src: str, dest: str, clone_func: Callable[[], None], timeout: float
) -> None:
    """Clone a repository with timeout.

    Args:
        src: clone source
        dest: clone destination
        clone_func: callable that does the actual cloning
        timeout: timeout in seconds
    """
    errors: Queue = Queue()
    process = Process(target=_clone_task, args=(clone_func, errors))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        # Give it literally a second (in successive steps of 0.1 second),
        # then kill it.
        # Can't use `process.join(1)` here, billiard appears to be bugged
        # https://github.com/celery/billiard/issues/270
        killed = False
        for _ in range(10):
            time.sleep(0.1)
            if not process.is_alive():
                break
        else:
            killed = True
            os.kill(process.pid, signal.SIGKILL)
        raise CloneTimeout(src, timeout, killed)

    if not errors.empty():
        raise CloneFailure(src, dest, errors.get())
