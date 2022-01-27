# This file is part of Sympathy for Data.
# Copyright (c) 2016 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import io
import os
import sys
import collections
import subprocess
import logging
import asyncio
import time
import itertools

from . task_worker2 import (
    datalines, decode_json, encode_json, setup_socket,
    NEW_TASK, NEW_QUIT_TASK, UPDATE_TASK, ABORT_TASK, DONE_TASK,
    SET_WORKERS_TASK, WORKER_CONNECTED
)
from sympathy.utils import log


tasks_logger = log.get_logger('core.tasks')
_module_file = os.path.abspath(__file__)


def encode_log_levels(log_levels):
    args = []
    for logger, level in log_levels.items():
        args.extend(['-L', logger, level])
    return args


class OrderedSet(object):
    def __init__(self):
        self._data = collections.OrderedDict()

    def add(self, value):
        self._data[value] = None

    def pop(self):
        value = self._data.popitem(last=False)[0]
        return value

    def remove(self, value):
        del self._data[value]

    def __iter__(self):
        return iter(self._data)

    def __bool__(self):
        return bool(self._data)

    def __nonzero__(self):
        return True if self._data else False


class Manager(object):
    """
    Manages workers and tasks.
    """

    def __init__(self, nworkers=1, environ=None, nocapture=False,
                 loglevel=None):
        self.worker_env = environ
        self.nocapture = nocapture
        self.loglevel = loglevel or {}
        self.bufl = []
        self.nworkers = nworkers
        self.blocked_workers = set()
        self.free_workers = OrderedSet()
        self.workers = set()
        self.wait_tasks = collections.OrderedDict()
        self.run_tasks = {}
        self.protocols = set()
        self._stopped = False
        self._worker_ids = itertools.count()
        self.worker_port = None

    def data_received(self, data):

        def get_msgs():
            lines = datalines(data, self.bufl)
            return [decode_json(line) for line in lines]

        self.input_msgs(get_msgs())

    def input_msgs(self, msgs):

        for msg in msgs:
            taskid, cmd, args = msg
            if cmd == NEW_TASK:
                self.add_task(msg, False)
            elif cmd == NEW_QUIT_TASK:
                self.add_task(msg, True)
            elif cmd == UPDATE_TASK:
                self.update_task(msg)
            elif cmd == ABORT_TASK:
                self.abort_task(taskid)
            elif cmd == SET_WORKERS_TASK:
                self.set_workers(args)
            else:
                assert False

    def output_msg(self, msg):
        taskid, cmd, args = msg
        if cmd in [UPDATE_TASK, DONE_TASK]:
            for protocol_ in self.protocols:
                protocol_.write(encode_json(msg) + b'\n')

    def add_task(self, task, quit_after):
        taskid, cmd, data = task
        tasks_logger.debug('Manager.add_task %s', taskid)
        if quit_after:
            self.start_worker()

        if self.free_workers:
            if taskid not in self.run_tasks:
                self.start_task(task)
        else:
            self.wait_tasks[taskid] = task

    def _schedule_task(self, task=None):
        if task:
            self.start_task(task)
        elif self.wait_tasks:
            task = self.wait_tasks.popitem(False)[1]
            self.start_task(task)

    def start_task(self, task):
        if self._stopped:
            return
        taskid, cmd, data = task
        free_worker = self.free_workers.pop()
        if cmd == NEW_QUIT_TASK:
            self.blocked_workers.add(free_worker)
        self.run_tasks[taskid] = (free_worker, task)
        free_worker.start_task(task)
        tasks_logger.debug('Manager.start_task %s, %s', taskid, free_worker)

    def reply_done_task(self, task):
        taskid, cmd, args = task
        tasks_logger.debug('Manager.reply_done_task %s', taskid)
        worker, task_ = self.run_tasks.pop(taskid, (None, None))
        if worker and task_:
            taskid, cmd, data = task_
            if worker in self.blocked_workers:
                self.stop_worker(worker)
            else:
                self.free_workers.add(worker)
                self._schedule_task()

        self.output_msg(task)

    def reply_update_task(self, task):
        self.output_msg(task)

    def update_task(self, task):
        taskid, cmd, data = task
        worker = self.run_tasks.get(taskid, [None])[0]
        if worker:
            worker.update_task(task)

    def abort_task(self, taskid):
        self.wait_tasks.pop(taskid, None)
        worker = self.run_tasks.get(taskid, [None])[0]
        if worker:
            blocked = worker in self.blocked_workers
            self.stop_worker(worker)
            if not blocked:
                self._start_worker_schedule_task()

    def worker_exited(self, worker, status):
        if self._stopped:
            return

        blocked = worker in self.blocked_workers
        if blocked:
            self.blocked_workers.remove(worker)

        if worker in self.workers:
            self.workers.remove(worker)

            if worker in self.free_workers:
                self.free_workers.remove(worker)
                self._start_worker_schedule_task()
            else:
                for taskid, (worker_, task) in list(self.run_tasks.items()):
                    if worker == worker_:
                        self.run_tasks.pop(taskid)
                        self.output_msg([taskid, DONE_TASK, status])
                        if not blocked:
                            self._start_worker_schedule_task()

    def start_worker(self):
        assert self.worker_port is not None, 'Worker port needs to be set'
        if not self._stopped:
            worker = Worker(self, next(self._worker_ids))
            worker.start()
            self.workers.add(worker)
            self.free_workers.add(worker)
            return worker

    def _start_worker_schedule_task(self):
        self.start_worker()
        self._schedule_task()

    def stop_worker(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)
            if worker in self.blocked_workers:
                self.blocked_workers.remove(worker)
            # Remove task before stopping worker.
            if worker in self.free_workers:
                self.free_workers.remove(worker)
            worker.stop()

    def set_workers(self, nworkers=None):
        self.nworkers = nworkers or self.nworkers
        self.blocked_workers = set(
            worker for worker, task in self.run_tasks.values())
        prev_free_workers = list(self.free_workers)
        self.free_workers = OrderedSet()
        for worker in prev_free_workers:
            if worker not in self.blocked_workers:
                self.stop_worker(worker)
        for i in range(self.nworkers):
            self._start_worker_schedule_task()

    def get_worker(self, worker_id):
        for worker in self.workers:
            if worker_id == worker.id:
                return worker

    def stop(self):
        self._stopped = True
        for worker in self.workers:
            self.blocked_workers.add(worker)
            worker.stop()

    def start(self):
        self.set_workers(self.nworkers)
        pass


class ManagerProtocol(asyncio.Protocol):
    def __init__(self, task_manager):
        self._tm = task_manager
        self.transport = None

    def connection_made(self, transport):
        tasks_logger.debug('ManagerProtocol.connection_made')
        self.transport = transport
        setup_socket(transport.get_extra_info('socket'))
        self._tm.protocols.add(self)

    def connection_lost(self, reason):
        tasks_logger.debug('ManagerProtocol.connection_lost')
        self._tm.protocols.remove(self)

    def data_received(self, data):
        self._tm.data_received(data)

    def write(self, data):
        self.transport.write(data)


class ManagerProtocolFactory(object):
    def __init__(self, task_manager):
        self._tm = task_manager

    def __call__(self):
        return ManagerProtocol(self._tm)


class Worker(object):
    """
    Manages a worker processes.
    """

    _script = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 'task_worker2.py'))

    def __init__(self, task_manager, worker_id):
        self._tm = task_manager
        self._worker_id = worker_id
        self._sub_transport = None
        self._pending_task = None
        self._exited = False
        self._status = None
        # Ready to accept new task, not updates.
        self._protocol_ready = False
        self.protocols = set()

    def _write_task(self, msg):
        if self._protocol_ready:
            for protocol_ in self.protocols:
                protocol_.write(encode_json(msg) + b'\n')
            self._protocol_ready = False
        else:
            self._pending_task = msg

    def input_msg(self, msg):
        if self.protocols:
            self._write_task(msg)
        else:
            assert self._pending_task is None
            self._pending_task = msg

    def start_task(self, task):
        self.input_msg(task)

    def update_task(self, task):
        if not self._protocol_ready:
            for protocol_ in self.protocols:
                protocol_.write(encode_json(task) + b'\n')

    def protocol_ready(self, protocol):
        assert (not self.protocols) or protocol in self.protocols
        self.protocols.add(protocol)
        self._protocol_ready = True
        if self._pending_task:
            pending_task = self._pending_task
            self._pending_task = None
            self._write_task(pending_task)

    def protocol_exited(self, protocol):
        self.protocols.remove(protocol)
        self._worker_exited()

    def exited(self, status):
        self._sub_transport.close()
        self._sub_transport = None
        self._exited = True
        self._status = status
        self._worker_exited()

    def _worker_exited(self):
        if self._exited and not self.protocols:
            # In case exited happens before protocol_exited:
            # Ensure time for worker to finish before removing worker.
            self._exited = None
            self._tm.worker_exited(self, self._status)

    def start(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self._start(), loop=loop)

    async def _start(self):
        loop = asyncio.get_event_loop()
        env = self._tm.worker_env or dict(os.environ)
        subprocess_co = loop.subprocess_exec(
            WorkerProcessProtocolFactory(self),
            *[
                sys.executable, '-u',
                self._script,
                str(self._worker_id),
                str(self._tm.worker_port), str(os.getpid()),
                str(int(self._tm.nocapture)),
                *encode_log_levels(self._tm.loglevel),
            ],
            bufsize=0,
            env=env)
        self._sub_transport, _ = await subprocess_co

    def stop(self):
        # Close kills the worker process.
        # TODO: check for possibility to support graceful shutdown.
        if self._sub_transport is not None:
            self._sub_transport.close()

    @property
    def id(self):
        if self._sub_transport:
            return self._worker_id


class WorkerProtocol(asyncio.Protocol):
    def __init__(self, task_manager):
        self._tm = task_manager
        self._worker = None
        self._bufl = []
        self.transport = None

    def connection_made(self, transport):
        tasks_logger.debug('WorkerProtocol.connection_made %s', self)
        self.transport = transport
        setup_socket(transport.get_extra_info('socket'))

    def connection_lost(self, reason):
        tasks_logger.debug('WorkerProtocol.connection_lost %s', self)
        if self._worker:
            self._worker.protocol_exited(self)

    def data_received(self, data):
        def get_msgs():
            lines = datalines(data, self._bufl)
            return [decode_json(line) for line in lines]
        msgs = get_msgs()

        for msg in msgs:
            taskid, cmd, args = msg
            if cmd == WORKER_CONNECTED:
                self._worker = self._tm.get_worker(args)
                if self._worker:
                    self._worker.protocol_ready(self)
            elif cmd == DONE_TASK:
                self._tm.reply_done_task(msg)
            elif cmd == UPDATE_TASK:
                self._tm.reply_update_task(msg)
            else:
                assert False

    def write(self, data):
        self.transport.write(data)


class WorkerProtocolFactory(object):
    def __init__(self, worker):
        self._worker = worker

    def __call__(self):
        return WorkerProtocol(self._worker)


class StdioSubprocessProtocol(asyncio.SubprocessProtocol):
    def __init__(self, *args, **kwargs):
        self._streams_and_writers = {
            1: self._get_stream_and_writer(sys.stdout),
            2: self._get_stream_and_writer(sys.stderr),
        }

    def _get_stream_and_writer(self, stream):
        binary = isinstance(stream, io.TextIOBase)

        if binary:
            stream = stream.buffer
            writer = self._binary_writer
        else:
            writer = self._text_writer
        return stream, writer

    def _binary_writer(self, stream, data):
        stream.write(data)
        stream.flush()

    def _text_writer(self, stream, data):
        stream.flush()
        data = data.decode('utf8', errors='replace')
        try:
            stream.write(data)
        except UnicodeDecodeError:
            stream.write(data.decode('ascii', errors='ignore'))
        stream.flush()

    def _write_stdio(self, fd, data):
        stream_and_writer = self._streams_and_writers.get(fd)
        if stream_and_writer:
            stream, writer = stream_and_writer
            writer(stream, data)


class WorkerProcessProtocol(StdioSubprocessProtocol):

    def __init__(self, worker):
        self._worker = worker
        self.transport = None
        self._pid = None
        super().__init__(binary=True)

    def connection_made(self, transport):
        self.transport = transport
        self._pid = transport.get_pid()
        tasks_logger.debug(
            'WorkerProcessProtocol.connection_made %s', self._pid)

    def connection_lost(self, reason):
        tasks_logger.debug(
            'WorkerProcessProtocol.connection_lost %s', self._pid)

    def process_exited(self):
        tasks_logger.debug(
            'WorkerProcessProtocol.process_exited %s', self._pid)
        exit_code = self.transport.get_returncode()
        self._worker.exited(exit_code or 0)

    def pipe_data_received(self, fd, data):
        self._write_stdio(fd, data)


class WorkerProcessProtocolFactory(object):
    def __init__(self, worker):
        self._worker = worker

    def __call__(self):
        return WorkerProcessProtocol(self._worker)


class Platform(object):
    """
    Manages the GUI/CLI application subprocess.
    """
    def __init__(self, exit_code_fut, port, args, env, stdin=None):
        self.exit_code_fut = exit_code_fut
        self.port = port
        self.args = args
        self.env = env
        self.stdin = stdin
        self._transport = None
        self.exit_code = 0

    def start(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self._start(), loop=loop)

    async def _start(self):
        loop = asyncio.get_event_loop()
        env = dict((self.env or dict(os.environ)).items())
        args = list(self.args)
        # Customizing cli order to match expected.
        args.insert(3, str(os.getpid()))
        args.insert(3, str(self.port))
        subprocess_co = loop.subprocess_exec(
            PlatformProcessProtocolFactory(self),
            sys.executable, '-u',
            *args,
            bufsize=0, env=env, stdin=self.stdin)

        self._transport, _ = await asyncio.ensure_future(
            subprocess_co, loop=loop)

    def exited(self, exit_code):
        self.exit_code = exit_code
        self._transport.close()
        self.exit_code_fut.set_result(exit_code)

    def stop(self):
        self._transport.close()

    def write(self, data):
        self._transport.write(data)


class PlatformProcessProtocol(StdioSubprocessProtocol):

    def __init__(self, platform):
        self._platform = platform
        self.bufl = []
        self.transport = None
        super().__init__()

    def connection_made(self, transport):
        tasks_logger.debug('PlatformProcessProtocol.connection_made')
        self.transport = transport

    def connection_lost(self, reason):
        tasks_logger.debug('PlatformProcessProtocol.connection_lost')

    def process_exited(self):
        tasks_logger.debug('PlatformProcessProtocol.process_exited')
        exit_code = self.transport.get_returncode()
        self._platform.exited(exit_code)

    def pipe_data_received(self, fd, data):
        self._write_stdio(fd, data)


class PlatformProcessProtocolFactory(object):

    def __init__(self, platform):
        self._platform = platform

    def __call__(self):
        return PlatformProcessProtocol(self._platform)


def start(platform_args, nworkers, worker_environ,
          platform_environ, nocapture, loglevel=None,
          pipe=False, external_platform=False):

    """
    Normal startup of application and subprocesses.

    Parameters
    ----------
    platform_args : list
        Arguments to the platform subprocess.
    nworkers : int
        Number of worker processes to use.
    worker_environ : dict
        environment to use in worker subprocess.
    platform_environ : dict
        environment to use in platform subprocess.
    nocapture : bool
        Disable capturing of worker output by the platform.
    loglevel : dict
        Log levels used by the platform subprocess.
    pipe : bool
        When set, connect stdin to platform subprocess in order
        to pass filenames that way.
    external_platform : bool
        When set, platform subprocess is not started by this function.
    """

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    platforms = []

    async def inner_loop():

        task_manager = Manager(
            nworkers, worker_environ, nocapture, loglevel)

        server_co = loop.create_server(
            WorkerProtocolFactory(task_manager), host='127.0.0.1')
        worker_server = await server_co
        worker_port = worker_server.sockets[0].getsockname()[1]
        task_manager.worker_port = worker_port

        server_co = loop.create_server(
            ManagerProtocolFactory(task_manager), host='127.0.0.1')
        platform_server = await server_co
        platform_port = platform_server.sockets[0].getsockname()[1]

        if not external_platform:
            stdin = sys.stdin if pipe else None
            exit_code_fut = loop.create_future()
            platform = Platform(exit_code_fut, platform_port,
                                platform_args,
                                platform_environ, stdin=stdin)
            platforms.append(platform)
            platform.start()
            task_manager.start()
            await exit_code_fut
            platform.stop()
            platform_server.close()
            task_manager.stop()
            worker_server.close()

            # Wait for stop.
            await asyncio.sleep(0)

            other = [task for task in asyncio.all_tasks()
                     if task is not asyncio.current_task()]
            await asyncio.gather(*other)
            loop.stop()
        else:
            task_manager.start()
            print('manager port:', str(platform_port))

    asyncio.ensure_future(inner_loop(), loop=loop)
    try:
        loop.run_forever()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        if platforms:
            sys.exit(platforms[0].exit_code)
        loop.close()

    sys.exit(-1)


def start_external(nworkers, worker_environ, nocapture,
                   stdout=None, stderr=None):
    """
    Special case startup intended for testing.
    """
    cwd = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), os.pardir))

    args = [sys.executable, '-u', '-c',
            'import sympathy.app.tasks.task_manager2; '
            'sympathy.app.tasks.task_manager2.start_external_manager()']

    if stdout is None:
        stdout = subprocess.PIPE
    if stderr is None:
        stderr = subprocess.STDOUT

    p = subprocess.Popen(
        args,
        cwd=cwd,
        stdout=stdout, stderr=stderr)

    while True:
        line = p.stdout.readline()
        time.sleep(0.1)
        if line.startswith(b'manager port: '):
            return p, int(line.split(b' ')[2].strip())
    return p


def start_external_manager():
    """
    Subprocess entrypoint for start_external.
    """
    logging.basicConfig()

    nworkers = 1
    worker_env = os.environ
    nocapture = False

    start(None, nworkers, worker_env, None, nocapture,
          external_platform=True)
