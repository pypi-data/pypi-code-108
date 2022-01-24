from __future__ import annotations
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from myqueue.config import Configuration
from myqueue.local import LocalScheduler, Server
from myqueue.submitting import submit_tasks
from myqueue.task import task as create_task
from myqueue.workflow import collect, run


@pytest.fixture(scope='function')
def scheduler(tmpdir):
    port = 39998
    dir = os.getcwd()
    home = Path(tmpdir)
    (home / '.myqueue').mkdir()
    config = Configuration('local', home=home)
    os.chdir(tmpdir)
    server = Server(config, port=port)
    thread = threading.Thread(target=server.start)
    thread.start()
    scheduler = LocalScheduler(config)
    import time
    time.sleep(0.5)
    scheduler.port = server.port
    yield scheduler
    scheduler.send('stop')
    thread.join()
    os.chdir(dir)


@pytest.mark.skipif(sys.version_info < (3, 8),
                    reason='requires Python 3.8 or higher')
def test_local_scheduler(scheduler):
    task1 = create_task('shell:sleep+10', tmax='1s')
    scheduler.submit(task1)
    task2 = create_task('shell:sleep+5')
    scheduler.submit(task2)
    ids = scheduler.get_ids()
    assert ids == ['1', '2']
    scheduler.cancel(task2)
    ids = scheduler.get_ids()
    assert ids == ['1']


def workflow():
    with run(shell='fail1', name='1'):
        run(shell='echo', name='2')
    with run(shell='fail2', name='3'):
        run(shell='echo', name='4')


@pytest.mark.skipif(sys.version_info < (3, 8),
                    reason='requires Python 3.8 or higher')
def test_local_scheduler2(scheduler):
    tasks = collect(workflow, Path())
    ok, ko, ex = submit_tasks(scheduler,
                              tasks,
                              current={},
                              force=False,
                              max_tasks=4,
                              verbosity=2,
                              dry_run=False)
    assert len(ok) == 4
    assert ex is None
    for i in range(10):
        if len(scheduler.get_ids()) == 0:
            break
        time.sleep(0.1)
    else:  # no break
        1 / 0
    names = set(path.name[6:]
                for path in Path('.myqueue').glob('local-*-?'))
    assert names == set(['1-2', '2-2', '2-0', '1-0'])
