from __future__ import annotations
import os
from pathlib import Path

from myqueue.test.flow1 import workflow
from myqueue.test.hello import workflow as hello


def test_flow1(mq):
    script = Path(__file__).with_name('flow1.py')
    mq(f'workflow {script}')
    mq.wait()
    assert mq.states() == 'ddddddd'
    mq(f'workflow {script}')
    mq.wait()
    assert mq.states() == 'dddddddd'


def test_direct_cached_flow1(tmp_path, capsys):
    os.chdir(tmp_path)
    a = workflow()
    assert a == 3
    assert capsys.readouterr().out == '\n'.join('0213243') + '\n'
    workflow()
    assert capsys.readouterr().out == ''


def test_workflow_old(mq):
    script = Path(__file__)
    mq(f'workflow {script}')


def test_hello(mq):
    Path('hello.sh').write_text('echo $@')
    script = Path(__file__).with_name('hello.py')
    mq(f'workflow {script}')
    mq.wait()
    assert mq.states() == 'dddddd'


def test_direct_hello(tmp_path):
    os.chdir(tmp_path)
    Path('hello.sh').write_text('echo $@')
    hello()


def test_flow2(mq):
    script = Path(__file__).with_name('flow2.py')
    mq(f'workflow {script}')
    mq.wait()
    assert mq.states() == 'MCCC'
    mq('rm -sC .')
    mq(f'workflow {script}')
    assert mq.states() == 'M'
    mq(f'workflow {script} --force')
    mq.wait()
    assert mq.states() == 'MCCC'
