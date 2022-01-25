import os
import re
import sys
import tempfile
import time


def remove_regex_capture_group_names(regex):
    # PostgreSQL will choke on named capture groups
    return re.sub(r'\?<\w+>', '', regex)


def pythonize_regex_capture_group_names(regex):
    # Unlike standard regex syntax, Python capture groups have a capital P:  (?P<group_name>.*?)
    return re.sub(r'\?<(\w+)>', r'?P<\1>', regex)


def replace_tokens_in_regex(regex, group_dict, escape=True):
    for name, value in group_dict.items():
        regex = regex.replace('${%s}' % name, re.escape(value) if escape else value)

    return regex


def os_lock(name, target, args=(), kwargs=None, timeout=7.0, retry_period=0.1):
    """
    Adapted from https://github.com/ses4j/backup/blob/master/oslockedaction.py
    To use, just wrap your python call with an os_lock() call.  Instead of:
    >>> time.sleep(5.0)
    Do:
    >>> os_lock(name="mylock", target=time.sleep, args=(5.0,))
    Nobody else using the same lockfile will be able to run at the same time.
    If timeout is None, it will never timeout if the lockfile exists.
    Otherwise it will just try to remove the lockfile after "timeout" seconds and do 'action()' anyway.
    retry_period is a float in seconds to wait between retries.
    """
    lockfile = os.path.abspath(os.path.join(tempfile.tempdir, f'{name}.lock'))

    f = None
    started_at = time.time()
    kwargs = dict() if kwargs is None else kwargs

    try:
        while True:
            if timeout is not None and time.time() > started_at + timeout:
                # timed out, it must be stale... (i hope)  so remove it.

                if time.time() > (started_at + (timeout * 2)):
                    raise RuntimeError(f"FAIL: os_lock() can't acquire directory lock, because {lockfile} was not "
                                       "cleaned up. Delete it manually if the process is finished.")

                try:
                    os.remove(lockfile)
                except OSError:
                    time.sleep(retry_period)
                    continue

            try:
                f = os.open(lockfile, os.O_RDWR | os.O_CREAT | os.O_EXCL)
                os.write(f, bytes(f'{str(__file__)} made this, called from {sys.argv[0]}', encoding='utf-8'))
                break
            except OSError:
                time.sleep(retry_period)

        target(*args, **kwargs)
    finally:
        if f:
            os.close(f)
            os.remove(lockfile)
