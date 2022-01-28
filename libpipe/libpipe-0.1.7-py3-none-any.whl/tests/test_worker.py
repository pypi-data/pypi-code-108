import os
import string
import random

from unittest import mock

from libpipe import worker


def test_worker(tmp_path):
    w = worker.WorkerPool([worker.localhost_shortname, 'test_node'], 'Test', max_tasks_per_worker=5)

    assert len(w.workers) == 10
    assert isinstance(w.workers[0].client, worker.LocalClient)
    assert isinstance(w.workers[6].client, worker.Client)

    w = worker.WorkerPool([worker.localhost_shortname], 'Test')

    for i in range(20):
        w.add('touch %s/t%d' % (str(tmp_path), i))

    success, errors = w.execute()

    assert len(success) == 20
    assert len(errors) == 0

    for i in range(20):
        assert os.path.isfile('%s/t%d' % (str(tmp_path), i))


def test_worker_log(tmp_path):
    w = worker.WorkerPool(['wrong_server', worker.localhost_shortname], 'Test')

    for i in range(20):
        w.add(f'echo Task {i}', output_file=str(tmp_path / f't{i}.log'))
        print(str(tmp_path / f't{i}.log'))

    success, errors = w.execute()

    assert len(success) == 20
    assert len(errors) == 0

    for i, task in enumerate(success):
        assert os.path.isfile(tmp_path / f't{i}.log')
        with open(tmp_path / f't{i}.log') as f:
            s = f.readlines()
        assert len(s) == 10 or len(s) == 8
        assert s[0].startswith('# Logging starting at ')
        assert s[1] == f'# Input command: echo Task {i}\n'
        if len(s) == 8:
            assert s[2] == f'Starting on host {task.process.client.host} with PID {task.process.process.pid}\n'
            assert s[4] == f'Task {i}\n'
        if len(s) == 10:
            assert s[2].startswith('Error')
            assert s[3] == f'Will retry 1 / 3 ...\n'
            assert s[4] == f'Starting on host {task.process.client.host} with PID {task.process.process.pid}\n'
            assert s[6] == f'Task {i}\n'
        assert s[-1].startswith('# Logging stopped at ')


def test_pidfile(tmp_path):
    w = worker.WorkerPool([worker.localhost_shortname], 'Test')

    for i in range(20):
        w.add(f'echo Task {i}; exit {i}', pid_filename=f't{i}.pid', keep_pid_file_on_error=True)

    success, errors = w.execute()

    assert len(success) == 20
    assert len(errors) == 0

    for task in success:
        assert os.path.exists(task.pid_filename) != (task.returncode == 0)
        if task.returncode > 0:
            with open(task.pid_filename) as fd:
                s = fd.read()
            assert s == f'{task.process.client.host} {task.process.process.pid}'


def test_worker_wrong_server(tmp_path):
    w = worker.WorkerPool(['wrong_server'] * 6, 'Test')

    for i in range(20):
        w.add(f'echo Task {i}')

    success, errors = w.execute()

    assert len(success) == 0
    assert len(errors) == 20


def test_worker_env_file(tmp_path):
    with open(tmp_path / 'env', 'w') as f:
        f.write('export WORKER_TEST=test_env')

    w = worker.WorkerPool([worker.localhost_shortname], 'Test', env_source_file=str(tmp_path / 'env'))

    os.listdir(tmp_path)

    for i in range(20):
        w.add('echo env:${WORKER_TEST}; touch %s/t_${WORKER_TEST}_%d' % (str(tmp_path), i))

    success, errors = w.execute()

    assert len(success) == 20
    assert len(errors) == 0

    for i in range(20):
        assert os.path.isfile('%s/t_test_env_%d' % (str(tmp_path), i))


def test_worker_retcode():
    w = worker.WorkerPool([worker.localhost_shortname], 'Test')

    w.add('set -e; cat non_existing_file', name=f't0')

    success, errors = w.execute()

    assert len(success) == 1
    assert len(errors) == 0
    assert success[0].returncode == 1

    w = worker.WorkerPool([worker.localhost_shortname], 'Test')

    for i in range(10):
        w.add(f'echo Task {i}; exit {i}', name=f't{i}')

    success, errors = w.execute()

    print([k.process.client for k in success])

    assert len(success) == 10
    assert len(errors) == 0
    assert [f't{k.returncode}' for k in success] == [k.name for k in success]


def test_timeout():
    w = worker.WorkerPool([worker.localhost_shortname], 'Test', max_time=2)

    w.add('echo 0')

    success, errors = w.execute()

    assert len(success) == 1
    assert len(errors) == 0

    w = worker.WorkerPool([worker.localhost_shortname], 'Test', max_time=1)

    w.add('sleep 100')

    success, errors = w.execute()

    # Currently falling. Need to be fixed
    assert len(success) == 0
    assert len(errors) == 1


def test_done_callback():
    w = worker.WorkerPool([worker.localhost_shortname], 'Test', max_time=2)

    done = False

    def callback():
        nonlocal done
        done = True

    w.add('echo 0', done_callback=callback)

    success, errors = w.execute()

    assert len(success) == 1
    assert len(errors) == 0
    assert done


class FakeSSHClient(worker.LocalClient):

    def __init__(self, host, user=None, force_sync=True, password=None):
        worker.LocalClient.__init__(self, force_sync=force_sync)
        self.host = host

    async def execute(self, task):
        await worker.LocalClient.execute(self, task)
        task.remote_host = self.host


def test_run_on_host():
    with mock.patch.object(worker, 'Client', FakeSSHClient):
        n_hosts = 10
        hosts = [f'host{k}' for k in range(n_hosts)]
        w = worker.WorkerPool(hosts, 'Test', max_time=2)

        for i in range(20 * n_hosts):
            w.add('echo 0', run_on_host=random.choice(hosts))

        success, errors = w.execute()

        assert len(errors) == 0

        for task in success:
            assert task.remote_host == task.run_on_host


def test_line_too_long(tmp_path):
    w = worker.WorkerPool([worker.localhost_shortname], 'Test')

    N = 100000
    s = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    log_file = str(tmp_path / f'text.log')

    w.add(f'echo Start; echo Other task; echo Done')
    w.add(f'echo Start; echo {s}; echo Done', output_file=log_file)
    w.add(f'echo Start; echo Other task; echo Done')

    success, errors = w.execute()

    has_long_line = False
    has_done = False

    with open(log_file) as f:
        for line in f.readlines():
            if '(line too long)' in line:
                has_long_line = True
            if 'Done' in line:
                has_done = True

    assert has_long_line
    assert has_done
    assert len(errors) == 0
    assert len(success) == 3
