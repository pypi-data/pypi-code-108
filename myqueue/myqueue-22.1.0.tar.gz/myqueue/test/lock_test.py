from __future__ import annotations
import pytest
from myqueue.utils import Lock


def test_lock(tmp_path):
    lockfile = tmp_path / 'lock'
    with Lock(lockfile):
        with pytest.raises(TimeoutError):
            with Lock(lockfile, timeout=0.07):
                pass
    assert not lockfile.is_file()
