from __future__ import annotations
import os
import shlex
from pathlib import Path

import pytest  # type: ignore

from myqueue.cli import _main
from myqueue.config import Configuration
from myqueue.queue import Queue
from myqueue.task import Task
from myqueue.test.scheduler import TestScheduler


@pytest.fixture(scope='function')
def mq(tmpdir):
    dir = os.getcwd()
    os.chdir(tmpdir)
    yield MQ(Path(tmpdir))
    os.chdir(dir)


test_config = """\
config = {
    'scheduler': 'test',
    'notifications': {
        'email': 'me@myqueue.org',
        'host': 'smtp.myqueue.org',
        'username': 'me'},
    'mpiexec': 'echo'}
"""


class MQ:
    def __init__(self, dir):
        mqdir = dir / '.myqueue'
        mqdir.mkdir()
        (mqdir / 'config.py').write_text(test_config)
        self.config = Configuration.read()
        self.scheduler = TestScheduler(self.config)
        TestScheduler.current_scheduler = self.scheduler
        os.environ['MYQUEUE_TESTING'] = str(dir)

    def __call__(self, cmd: str, error: int = 0) -> None:
        args = shlex.split(cmd)
        if args and args[0][0] != '-' and args[0] != 'help':
            args[1:1] = ['--traceback']
        print(f'$ mq {cmd}')
        for i, arg in enumerate(args):
            if '*' in arg:
                args[i:i + 1] = sorted([str(p) for p in Path().glob(arg)])
                break
        err = _main(args)
        assert err == error

    def states(self) -> str:
        return ''.join(task.state.value
                       for task in mqlist(self.scheduler.config))

    def wait(self) -> None:
        while True:
            done = self.scheduler.kick()
            if done:
                break


def mqlist(config) -> list[Task]:
    with Queue(config, verbosity=0) as q:
        q._read()
        return q.tasks
