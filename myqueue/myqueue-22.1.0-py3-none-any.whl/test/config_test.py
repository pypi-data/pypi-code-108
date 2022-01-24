from __future__ import annotations
import pytest
from myqueue.config import Configuration


def test_config():
    cfg = Configuration('test')
    print(cfg)
    print(repr(cfg))


def test_missing_or_deprecated_key(mq):
    cfg_file = mq.config.home / '.myqueue/config.py'
    cfg_file.write_text('config = {}\n')
    with pytest.raises(ValueError):
        Configuration.read()
    cfg_file.write_text("config = {'scheduler': 'test', 'mpi': 'openmpi'}\n")
    with pytest.warns(UserWarning):
        Configuration.read()
