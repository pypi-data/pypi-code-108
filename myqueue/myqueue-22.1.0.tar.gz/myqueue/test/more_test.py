from __future__ import annotations
import sys
import subprocess
from pathlib import Path

import pytest

from ..queue import Queue
from ..task import task
from myqueue.progress import main


def test_progress():
    main(0.0)


@pytest.mark.skipif(sys.version_info < (3, 9),
                    reason='requires Python 3.9 or higher')
def test_completion():
    from myqueue.utils import update_readme_and_completion
    update_readme_and_completion(test=True)


def test_api(mq):
    from myqueue import submit
    from myqueue.task import task
    submit(task('myqueue.test@oom 1'))
    submit(task('myqueue.test@timeout_once', tmax='1s'))
    mq.wait()
    submit(task('myqueue.test@timeout_once'))
    mq.wait()
    assert mq.states() == 'MTd'


def test_logo():
    from myqueue.logo import create
    create()


def test_backends(mq):
    from ..config import guess_configuration, guess_scheduler
    config = mq.scheduler.config
    config.nodes = [('abc16', {'cores': 16, 'memory': '16G'}),
                    ('abc8', {'cores': 8, 'memory': '8G'})]
    config.mpiexec = 'echo'
    for name in ['slurm', 'lsf', 'pbs']:
        print(name)
        if name == 'pbs':
            p = Path('venv/bin/')
            p.mkdir(parents=True)
            (p / 'activate').write_text('')
        config.scheduler = name
        with Queue(config, dry_run=True, verbosity=2) as q:
            q.submit([task('shell:echo hello', cores=24)])

    guess_scheduler()
    guess_configuration('local')


class Result:
    def __init__(self, stdout):
        self.stdout = stdout


def run(commands, stdout):
    if commands[0] == 'sinfo':
        return Result(b'8 256000+ xeon8*\n')
    return Result(b'id state 8:8 load xeon8 128 G\n')


def test_autoconfig(monkeypatch):
    from ..scheduler import get_scheduler
    from ..config import Configuration

    monkeypatch.setattr(subprocess, 'run', run)
    nodes, _ = get_scheduler(Configuration('slurm')).get_config()
    assert nodes == [('xeon8', 8, '256000M')]

    nodes, _ = get_scheduler(Configuration('LSF')).get_config()
    assert nodes == [('xeon8', 8, '128G')]


def test_commands():
    from ..commands import ShellScript, convert, create_command
    assert convert('True') is True
    assert convert('False') is False
    assert convert('3.14') == 3.14
    assert convert('42') == 42
    cmd = create_command('./script.sh 1 2')
    assert isinstance(cmd, ShellScript)
    assert cmd.todict()['args'] == ['1', '2']
    print(cmd)


def test_resource_comments(tmp_path):
    from ..task import task
    script = tmp_path / 'script.py'
    script.write_text('# Script\n# MQ: resources=2:1h\n')
    t = task(str(script))
    assert t.resources.cores == 2
    assert t.resources.tmax == 3600
