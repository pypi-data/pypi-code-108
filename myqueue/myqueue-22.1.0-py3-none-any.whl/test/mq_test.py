from __future__ import annotations
import shutil
import time
from pathlib import Path

from ..utils import chdir

LOCAL = True


def test_submit_args(mq):
    mq('''submit "myqueue.test.mod --opt={...,x={'y':(1,2)}"''')
    mq.wait()
    assert mq.states() == 'd'


def test_submit(mq):
    f = Path('folder')
    f.mkdir()
    mq('submit time@sleep+0.1 . folder --max-tasks=9')
    mq('submit shell:echo+hello -d time@sleep+0.1')
    mq.wait()
    assert mq.states() == 'ddd'
    shutil.rmtree(f)
    mq('sync')
    assert mq.states() == 'dd'
    mq('daemon status')


def test_fail(mq):
    mq('submit time@sleep+a')
    mq('submit shell:echo+hello -d time@sleep+a')
    mq('submit shell:echo+hello2 -d shell:echo+hello')
    mq.wait()
    mq('info')
    mq('info -i1 -v')
    mq('ls -S t')
    mq('ls -L')
    assert mq.states() == 'FCC', mq.states()
    mq('resubmit -sF . -z')
    assert mq.states() == 'FCC'
    mq('resubmit -sF .')
    mq.wait()
    assert mq.states() == 'CCF'
    mq('modify -s F -N T .')
    assert mq.states() == 'CCT'


def test_fail2(mq):
    mq('submit time@sleep+a --workflow')
    mq.wait()
    assert mq.states() == 'F'
    mq('remove --states F .')
    mq('submit time@sleep+a --workflow')
    mq.wait()
    assert mq.states() == ''


def test_timeout(mq):
    t = 3 if LOCAL else 120
    mq(f'submit -n zzz "shell:sleep {t}" -R 1:1s')
    mq('submit "shell:echo hello" -d zzz')
    mq.wait()
    mq('resubmit -sT . -R 1:5m')
    mq.wait()
    assert mq.states() == 'Cd'


def test_timeout2(mq):
    t = 3 if LOCAL else 120
    mq(f'submit "shell:sleep {t}" -R1:{t // 3}s --restart 2')
    mq(f'submit "shell:echo hello" -d shell:sleep+{t}')
    mq.wait()
    mq('ls')
    mq('kick')
    mq('ls')
    mq.wait()
    if mq.states() != 'dd':
        mq('kick')
        mq.wait()
        assert mq.states() == 'dd'


def test_oom(mq):
    mq(f'submit "myqueue.test@oom {LOCAL}" --restart 2')
    mq.wait()
    assert mq.states() == 'M'
    mq('kick')
    mq.wait()
    assert mq.states() == 'd'


wf = """
from myqueue.task import task
def create_tasks():
    t1 = task('shell:sleep+3')
    t2 = task('shell:touch+hello', deps=[t1], creates=['hello'])
    return [t1, t2]
"""


def test_workflow(mq):
    mq('submit shell:sleep+3 -R1:1m -w')
    time.sleep(2)
    Path('wf.py').write_text(wf)
    mq('workflow wf.py . -t shell:touch+hello')
    mq.wait()
    assert mq.states() == 'dd'
    mq('workflow wf.py .')
    assert mq.states() == 'dd'
    mq('rm -s d .')
    Path('shell:touch+hello.state').unlink()
    mq('workflow wf.py .')
    mq.wait()
    assert mq.states() == ''
    hello = Path('hello')
    hello.unlink()
    mq('workflow wf.py .')
    mq.wait()
    assert mq.states() == 'd'
    assert hello.is_file()


def test_workflow_running_only_with_targets(mq):
    Path('wf.py').write_text(wf)
    mq('workflow wf.py . -t shell:touch+hello')
    mq.wait()
    assert mq.states() == 'dd'


def test_workflow_with_failed_job(mq):
    Path('wf.py').write_text(wf)
    failed = Path('shell:sleep+3.state')
    failed.write_text('{"state": "FAILED"}\n')
    mq('workflow wf.py .')
    mq.wait()
    assert mq.states() == ''

    mq('workflow wf.py . --force --dry-run')
    mq.wait()
    assert mq.states() == ''
    assert failed.read_text() == '{"state": "FAILED"}\n'

    mq('workflow wf.py . --force')
    mq.wait()
    assert mq.states() == 'dd'
    assert failed.read_text() == '{"state": "done"}\n'


wf2 = """
from myqueue.task import task
def create_tasks(name, n):
    assert name == 'hello'
    assert n == 5
    return [task('shell:echo+hi', diskspace=1) for _ in range(4)]
"""


def test_workflow2(mq):
    Path('wf2.py').write_text(wf2)
    mq('workflow wf2.py . -a name=hello,n=5')
    mq('kick')
    mq.wait()
    assert mq.states() == 'dddd'


def test_cancel(mq):
    mq('submit shell:sleep+2')
    mq('submit shell:sleep+999')
    mq('submit shell:echo+hello -d shell:sleep+999')
    mq('rm -n shell:sleep+999 -srq .')
    mq.wait()
    assert mq.states() == 'd'


def test_check_dependency_order(mq):
    mq('submit myqueue.test@timeout_once -R 1:1s --restart 1')
    mq('submit shell:echo+ok -d myqueue.test@timeout_once --restart 1')
    mq.wait()
    assert mq.states() == 'TC'
    mq('kick')
    mq.wait()
    assert mq.states() == 'dd'


def test_run(mq):
    mq('run "math@sin 3.14" . -z')
    mq('run "math@sin 3.14" .')
    mq('submit "time@sleep 1"')
    mq('run "time@sleep 1" .')
    mq.wait()
    assert mq.states() == ''


def test_misc(mq):
    f = Path('subfolder')
    f.mkdir()
    with chdir(f):
        mq('init')
    mq('help')
    mq('ls -saA')
    mq('-V')
    mq('completion')
    mq('ls no_such_folder', error=1)
    mq('')
    mq('info -A')


def test_sync_kick(mq):
    mq('sync')
    mq('kick')


def test_slash(mq):
    mq('submit "shell:echo a/b"')
    mq('submit "shell:echo a/c" -w')
    mq.wait()
    assert mq.states() == 'dd'


def test_config(mq):
    mq('config local')


def test_more_homes(mq):
    f = Path('folder')
    f.mkdir()
    with chdir(f):
        mq('init')
    mq('submit shell:echo . folder', error=1)
