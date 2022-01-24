from dataclasses import dataclass
from itertools import product
from pathlib import Path
from random import Random

import pytest

from atqo.distributed_apis import DIST_API_MAP
from atqo.lock_stores import (
    SEPARATOR,
    STORE_DICT,
    LockStoreBase,
    get_lock_store,
)
from atqo.simplified_functions import parallel_map


@dataclass
class IoArg:
    path: Path
    add: int

    @classmethod
    def from_args(cls, args):
        return cls(*args)


class Writer:
    def __init__(self, lock_store: LockStoreBase) -> None:
        self._locks = lock_store

    def __call__(self, arg: IoArg):
        with self._locks.get(arg.path.as_posix()):
            i = int(arg.path.read_text())
            arg.path.write_text(str(i + arg.add))


@pytest.mark.parametrize(
    ["store_key", "size", "nfiles", "dkey"],
    product(STORE_DICT.keys(), [5, 50, 500], [2, 30], DIST_API_MAP.keys()),
)
def test_para_io(tmp_path, store_key, size, nfiles, dkey):

    rng = Random(120)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_files = [data_dir / f"file-{i}" for i in range(nfiles)]
    for df in data_files:
        df.write_text("0")

    lockstr = f"{store_key}{SEPARATOR}{tmp_path / 'locks'}"
    lock_store = get_lock_store(lockstr)

    args = [*product(data_files, range(size))]
    rng.shuffle(args)

    parallel_map(
        Writer(lock_store),
        map(IoArg.from_args, args),
        dkey,
    )

    for fp in data_files:
        assert int(fp.read_text()) == sum(range(size))
