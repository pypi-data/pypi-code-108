from __future__ import annotations
import os
from myqueue.utils import convert_done_files


def test_convert_done_files(tmp_path):
    (tmp_path / 't1.done').write_text('')
    (tmp_path / 't2.done').write_text('[117]')
    os.chdir(tmp_path)
    convert_done_files()
    t1 = (tmp_path / 't1.state').read_text()
    t2 = (tmp_path / 't2.state').read_text()
    assert t1 == '{"state": "done"}\n'
    assert t2 == '{"state": "done",\n "result": [117]}\n'
