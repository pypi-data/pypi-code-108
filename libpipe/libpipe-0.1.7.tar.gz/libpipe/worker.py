# Multi-process, multi-nodes process executors
#
# Authors: F.Mertens

import os
import re
import sys
import time
import socket
import signal
import getpass
import asyncio
import datetime
import itertools
import collections
from enum import Enum

import asyncssh
import progressbar
from click import style, secho


localhost_shortname = socket.gethostname().split('.', 1)[0]


def kill_remote(host, user, pid):
    os.system(f'ssh {user}@{host} "kill -TERM -{pid}"')


def n_digits(i):
    return len(str(i))


def expend_num_ranges(s):
    r = re.split(r'\[([0-9-,]+)\]', s)
    for i in range(1, len(r), 2):
        if ',' in r[i]:
            r[i] = r[i].split(',')
        elif '-' in r[i]:
            s, e = r[i].split('-')
            n = max(n_digits(s), n_digits(e))
            r[i] = [str(k).rjust(n, '0') for k in range(int(s), int(e) + 1)]
    for i in range(0, len(r), 2):
        r[i] = [r[i]]
    for el in itertools.product(*r):
        yield ''.join(el)


def get_hosts(host_string):
    hosts = list(set(host for k in host_string.split(',') for host in expend_num_ranges(k)))
    return [localhost_shortname if h == 'localhost' else h for h in hosts]


def get_worker_pool(name, nodes='localhost', max_concurrent=4, env_file=None, max_time=None,
                    debug=False, dry_run=False):
    hosts = get_hosts(nodes)
    return WorkerPool(hosts, name=name, max_tasks_per_worker=max_concurrent,
                      env_source_file=env_file, max_time=max_time, debug=debug, dry_run=dry_run)


class TaskStatus(Enum):
    WAITING = 1
    RUNNING = 2
    CANCELED = 3
    SUCCESS = 4
    ERROR = 5


class WorkerStatus(Enum):
    IDLE = 1
    COMMITED = 2
    RUNNING = 3
    ERROR = 4
    CLOSED = 5


class Process(object):

    def __init__(self, client, process):
        self.client = client
        self.process = process


class Task(object):
    """Represent a task executed by the worker pool

    Attributes:
        name (str): Name of the task (set by the worker pool).
        command (str): Command
        output_file (str): Optional log file. None if not set.
        returncode (int): Return code. None if task was not executed.
    """

    def __init__(self, name, command, output_file=None, done_callback=None, 
                 run_on_host=None, n_try=3, pid_filename=None, keep_pid_file_on_error=False):
        self.name = name
        self.command = command
        self.output_file = output_file
        self.fd = None
        self.returncode = None
        self.n_try = 0
        self.done_callback = done_callback
        self.run_on_host = run_on_host
        self.status = TaskStatus.WAITING
        self.process = None
        self.n_try = n_try
        self.timed_out = False
        self.pid_filename = pid_filename
        self.keep_pid_file_on_error = keep_pid_file_on_error

    def init_log(self):
        if self.output_file is not None:
            self.fd = open(self.output_file, 'w')
            self.fd.write(f'# Logging starting at {datetime.datetime.now()}\n')
            self.fd.write(f'# Input command: {self.command}\n')

    def set_process(self, process):
        self.process = process
        if hasattr(self.process.process, 'pid'):
            self.log(f'Starting on host {self.process.client.host} with PID {self.process.process.pid}\n\n', 
                     self.process.client.host)
            if self.pid_filename is not None:
                try:
                    with open(self.pid_filename, 'w') as fd:
                        fd.write(f'{self.process.client.host} {self.process.process.pid}')
                    self.log(f'Starting on host {self.process.client.host} with PID {self.process.process.pid}\n\n',
                             self.process.client.host)
                except Exception:
                    self.log(f'Error creating PID file {self.pid_filename}', self.process.client.host, err=True)

    async def terminate(self):
        if self.process is not None and hasattr(self.process.process, 'pid'):
            if self.process.client.host is localhost_shortname:
                self.log(f'Killing local process PID {self.process.process.pid}\n', 'local', err=True)
                try:
                    os.killpg(os.getpgid(self.process.process.pid), signal.SIGTERM)
                except ProcessLookupError:
                    print(f'Process {self.process.process.pid} not found')
            else:
                self.log(f'Killing remote process PID {self.process.process.pid}\n', self.process.client.host, err=True)
                kill_remote(self.process.client.host, self.process.client.user, self.process.process.pid)

    def log(self, line, host, err=False):
        if isinstance(line, bytes):
            line = line.decode()
        if self.fd is not None:
            self.fd.write(line)
        line = line.strip()
        if err:
            line = style(line, fg='red')
        print(f'[{self.name}:{host}] {line}')

    async def log_stream(self, stream, host, err=False):
        while True:
            try:
                async for line in stream:
                    self.log(line, host, err=err)
            except ValueError:
                self.log('(line too long)', host, err=True)
                continue
            break

    def close_log(self):
        if self.pid_filename and os.path.exists(self.pid_filename):
            if not self.keep_pid_file_on_error or self.returncode == 0:
                os.remove(self.pid_filename)
        if self.fd is not None:
            try:
                self.fd.write(f'\n\n# Logging stopped at {datetime.datetime.now()} with code: {self.returncode}\n')
                self.fd.close()
            except Exception:
                print(f'Error closing log file for task {self.name}. Ignoring.')

    async def run(self, client_pool):
        self.init_log()

        for i in range(self.n_try):
            self.timed_out = False

            worker = await client_pool.get_worker(self.run_on_host)
            self.status = TaskStatus.RUNNING

            ret_status, err_msg = await worker.run(self)

            if err_msg:
                self.log(err_msg, worker.client.host, err=True)

            if ret_status and not self.timed_out:
                self.status = TaskStatus.SUCCESS
                break

            self.status = TaskStatus.ERROR
            if i + 1 < self.n_try:
                self.log(f'Will retry {i + 1} / {self.n_try} ...\n', worker.client.host, err=True)

        self.close_log()


class SSHClient(asyncssh.SSHClient):

    def __init__(self):
        self.connected = False

    def connection_made(self, conn):
        self.connected = True
        print('Connection made to %s.' % conn.get_extra_info('peername')[0])

    def connection_lost(self, exc):
        if exc:
            print('SSH client error: ' + str(exc))
            raise exc
        self.connected = False


class Client(object):

    def __init__(self, host, user=None, force_sync=True, password=None):
        self.host = host
        self.user = user
        self.password = password
        self.conn = None
        self.client = None
        self.starting = False
        self.started = asyncio.Event()
        self.closing = False
        self.force_sync = force_sync
        self.creating_session = asyncio.Lock()

    async def start(self):
        if not self.starting:
            self.starting = True
            print(f'Starting client {self.host} ...')
            try:
                self.conn, self.client = await asyncssh.create_connection(SSHClient, self.host, username=self.user,
                                                                          password=self.password)
            except Exception:
                raise
            finally:
                self.started.set()

    async def execute(self, task):
        if not self.connected():
            raise ConnectionError('Client not connected')

        async with self.creating_session:
            process = await self.conn.create_process('echo $$;' + task.command)
        
        try:
            process.pid = int(await process.stdout.readline())
        except ValueError:
            task.log('Error retrieving PID of remote process', self.host, err=True)

        task.set_process(Process(self, process))

        await task.log_stream(process.stdout, self.host)
        await task.log_stream(process.stderr, self.host, err=True)

        process.channel.close()
        task.returncode = process.returncode

        if self.force_sync:
            await self.conn.run('sync')
            await asyncio.sleep(1)

    def close(self):
        if self.conn is not None and not self.closing:
            self.closing = True
            self.conn.close()
            self.conn = None

    def connected(self):
        return self.client is not None and self.client.connected


class LocalClient(object):

    def __init__(self, host='local', force_sync=True):
        self.host = host
        self.started = asyncio.Event()
        self.force_sync = force_sync

    async def start(self):
        self.started.set()

    async def execute(self, task):
        process = await asyncio.create_subprocess_shell(task.command, stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE, preexec_fn=os.setpgrp)
        task.set_process(Process(self, process))

        await task.log_stream(process.stdout, self.host)
        await task.log_stream(process.stderr, self.host, err=True)

        task.returncode = await process.wait()

        if self.force_sync:
            os.sync()
            await asyncio.sleep(1)

    def connected(self):
        return self.started.is_set()

    def close(self):
        # nothing to do
        pass


class Worker(object):

    def __init__(self, client, name):
        self.client = client
        self.name = name
        self.status = WorkerStatus.IDLE
        self.execute_start_time = None
        self.running_task = None

    async def run(self, task):
        self.running_task = task
        self.execute_start_time = time.time()
        self.status = WorkerStatus.RUNNING
        err_msg = ''

        try:
            await self.client.start()
        except Exception as exc:
            err_msg = f'Error starting client: {str(exc)}\n'
            self.status = WorkerStatus.ERROR
            return False, err_msg

        await self.client.started.wait()

        try:
            await self.client.execute(task)
        except ConnectionError as exc:
            err_msg = f'Error connecting client: {str(exc)}\n'
            self.status = WorkerStatus.ERROR
            return False, err_msg
        except asyncio.CancelledError:
            err_msg = f'Task {self.name} has been canceled\n'
            return True, err_msg
        except Exception as exc:
            err_msg = f'Error executing task {self.name}: {str(exc)}\n'
            self.status = WorkerStatus.IDLE
            return False, err_msg

        if task.done_callback is not None:
            try:
                task.done_callback()
            except Exception as exc:
                err_msg = f'Error executing return callback of task {self.name}: {str(exc)}\n'

        self.status = WorkerStatus.IDLE

        return True, err_msg

    def close(self):
        self.status = WorkerStatus.CLOSED
        self.client.close()


class WorkerPool(object):

    def __init__(self, hosts, name='Worker', max_tasks_per_worker=4,
                 env_source_file=None, user=None, max_time=None, force_sync=False,
                 debug=False, dry_run=False, password=None):
        """Initiate a worker pool.

        Args:
            name (str): Name of the worker pool.
            hosts (list): List of host names, reachable via ssh (if not local host).
            max_tasks_per_worker (int, optional): Maximum number of tasks to execute concurrently on an host.
            env_source_file (str, optional): Name of a file to source before executing a task.
            user (str, optional): User to connect
        """
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())

        if user is None:
            user = getpass.getuser()

        self.workers = []
        self.tasks = []
        self.env_file = env_source_file
        self.max_time = max_time
        self.name = name
        self.debug = debug
        self.dry_run = dry_run
        self.hosts = hosts
        self.futures = None
        self.active_hosts = hosts

        for host in self.hosts:
            if host == localhost_shortname:
                client = LocalClient(localhost_shortname, force_sync=force_sync)
            else:
                client = Client(host, user, force_sync=force_sync, password=password)

            for i in range(max_tasks_per_worker):
                worker = Worker(client, f'{client.host}:{i}')
                self.workers.append(worker)

        widgets = [
            f"{style(self.name, bold=True)}: ", progressbar.Percentage(), ' (',
            progressbar.SimpleProgress(), ')'
            ' ', progressbar.Bar(marker='|', left='[', right=']'),
            ' ', progressbar.Timer(),
            ' ', progressbar.ETA(),
        ]

        self.pbar = progressbar.ProgressBar(redirect_stdout=True, widgets=widgets)

    async def get_worker(self, host=None):
        while True:
            for worker in self.workers:
                if host is not None and worker.client.host != host:
                    if host not in self.active_hosts:
                        print(f'Requested run_on_host "{host}" not available anymore. Releasing constraint ...')
                        host = None
                    continue
                if worker.status is WorkerStatus.IDLE:
                    worker.status = WorkerStatus.COMMITED
                    return worker
            await asyncio.sleep(0.1)

    def add(self, command, name=None, output_file=None, done_callback=None, 
            run_on_host=None, n_try=3, pid_filename=None, keep_pid_file_on_error=False):
        """Add a command to execute by a worker in the pool. Optionally output result in output_file.

        Args:
            command (str): Command to execute.
            name (str, optional): Name of the task. If not set it will be set by the worker pool
            output_file (str, optional): Optional filename to log output into.
        """
        if run_on_host is not None and run_on_host not in self.hosts:
            print(f'Requested run_on_host "{run_on_host}" is not in the hosts list. Releasing constraint ...')

        if self.env_file:
            command = "bash -c '. %s; %s'" % (self.env_file, command)
        if name is None:
            name = f'T{len(self.tasks)}'

        if self.debug:
            print(command)
        if self.dry_run:
            return

        self.tasks.append(Task(name, command, output_file=output_file, done_callback=done_callback,
                               run_on_host=run_on_host, n_try=n_try, pid_filename=pid_filename, 
                               keep_pid_file_on_error=keep_pid_file_on_error))

    def get_all_tasks(self):
        tasks = collections.defaultdict(list)
        for t in self.tasks:
            tasks[t.status].append(t)
        return tasks

    async def _monitor_queue(self, update_interval=1):
        try:
            n_todo = len(self.tasks)
            while n_todo > 0:
                await asyncio.sleep(update_interval)
                tasks = self.get_all_tasks()
                n_done = len(tasks[TaskStatus.SUCCESS])
                n_todo = len(tasks[TaskStatus.WAITING]) + len(tasks[TaskStatus.RUNNING])
                self.pbar.update(n_done)

                self.active_hosts = set(w.client.host for w in self.workers if w.status != WorkerStatus.ERROR)
                n_active_workers = 0

                for worker in self.workers:
                    n_active_workers += worker.status != WorkerStatus.ERROR

                    if worker.status == WorkerStatus.RUNNING and self.max_time is not None:
                        running_time = time.time() - worker.execute_start_time
                        if running_time > (self.max_time + update_interval):
                            task = worker.running_task
                            task.timed_out = True
                            task.log(f'Task timeout: waited for {running_time:.2f} s', worker.client.host, err=True)
                            task.log(f'Command was: {task.command}', worker.client.host, err=True)
                            await task.terminate()

                if n_active_workers == 0:
                    secho("No active workers, canceling all remaining tasks ...", fg='red')
                    if self.futures is not None:
                        for future in self.futures[::-1]:
                            future.cancel()

        except asyncio.CancelledError:
            pass

    async def terminate_all(self):
        for worker in self.workers:
            worker.close()
        for task in self.tasks:
            if task.status == TaskStatus.RUNNING:
                await task.terminate()
        if self.futures is not None:
            for task in self.futures:
                task.cancel()

    async def shutdown(self, exit_code=0):
        await self.terminate_all()
        await asyncio.sleep(0.5)

        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(sys.exit, exit_code)

    async def process_tasks(self):
        self.pbar.start(max_value=len(self.tasks))

        self.futures = [asyncio.ensure_future(task.run(self)) for task in self.tasks]
        self.futures.append(asyncio.ensure_future(self._monitor_queue()))

        await asyncio.gather(*self.futures, return_exceptions=False)

    def execute(self):
        if not self.tasks:
            self.pbar.finish()
            return [], []

        loop = asyncio.get_event_loop()

        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.shutdown(exit_code=1)))

        try:
            loop.run_until_complete(self.process_tasks())
        except KeyboardInterrupt:
            loop.run_until_complete(self.terminate_all())
            raise
        except asyncio.CancelledError:
            secho(f'Error: one (or more) task(s) have been canceled', fg='red')
        finally:
            for worker in self.workers:
                worker.close()

        tasks = self.get_all_tasks()
        n_success = len(tasks[TaskStatus.SUCCESS])

        self.pbar.update(n_success)
        self.pbar.finish(dirty=n_success != len(self.tasks))

        return tasks[TaskStatus.SUCCESS], tasks[TaskStatus.ERROR] + tasks[TaskStatus.CANCELED] \
            + tasks[TaskStatus.WAITING] + tasks[TaskStatus.RUNNING]
