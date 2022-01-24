from __future__ import annotations
from myqueue.resources import Resources


def test_res():
    r = '16:1:xeon8:2h'
    r1 = Resources.from_args_and_command(resources=r)
    r2 = Resources.from_string(r)
    assert str(r1) == str(r2)
