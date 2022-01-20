from contextlib import contextmanager
from time import monotonic

from django.core.cache import cache

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


@contextmanager
def global_lock(lock_id, value=1, expire=LOCK_EXPIRE):
    """
    Global lock mechanizm.

    Idea from
    http://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html
    """
    timeout_at = monotonic() + expire - 3
    lock_key = build_global_cache_key(lock_id)
    # cache.add fails if the key already exists
    status = cache.add(lock_key, value, expire)
    try:  # noqa: WPS501
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else.
            cache.delete(lock_key)


def build_global_cache_key(lock_id):
    """Function for build global lock key."""
    return "____{0}____".format(lock_id)
