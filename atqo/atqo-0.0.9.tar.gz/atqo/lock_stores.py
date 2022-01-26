from abc import abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from typing import Optional

SEPARATOR = "://"


class LockStoreBase:
    @abstractmethod
    def __init__(self, initstr: str) -> None:
        pass  # pragma: no cover

    def acquire(self, key) -> Lock:
        lock = self.get(key)
        lock.acquire()
        return lock

    @abstractmethod
    def get(self, key: str) -> Lock:
        pass  # pragma: no cover


class FileLockStore(LockStoreBase):
    def __init__(self, initstr: str) -> None:

        from filelock import FileLock

        self._lock_cls = FileLock

        self.root = initstr or TemporaryDirectory().name

    def get(self, key) -> Lock:
        return self._lock_cls(self._get_path(key))

    def _get_path(self, key):
        try:
            subpath = Path(key).relative_to(Path(self.root).root)
        except ValueError:
            subpath = Path(key)
        path = Path(self.root, subpath)
        path.parent.mkdir(exist_ok=True, parents=True)
        return path


STORE_DICT = {
    # "local": ThreadLockStore,
    # "redis": RedisLockStore,
    # "dask": DaskLockStore,
    "file": FileLockStore,
}

DEFAULT_STORE_STR = [*STORE_DICT.keys()][-1] + SEPARATOR


def get_lock_store(store_str: Optional[str] = None) -> LockStoreBase:
    f"""get a lock store based on a string

    Parameters
    ----------
    store_str : str
       {', '.join([f'{k}{SEPARATOR}initstr' for k in STORE_DICT.keys()])}

    where initstr is passed to the matching LockStore:

    {STORE_DICT}

    Returns
    -------
    LockStoreBase
        one of {[*STORE_DICT.values()]}
    """
    prefix, initstr = (store_str or DEFAULT_STORE_STR).split(SEPARATOR)
    return STORE_DICT[prefix](initstr)
