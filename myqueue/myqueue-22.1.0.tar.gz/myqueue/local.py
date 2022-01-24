from __future__ import annotations
import asyncio
import pickle
import socket
from functools import partial
from typing import Any

from .scheduler import Scheduler
from .task import Task
from .config import Configuration
from .states import State
from myqueue.queue import Queue


class LocalSchedulerError(Exception):
    pass


class LocalScheduler(Scheduler):
    port = 39999

    def submit(self,
               task: Task,
               dry_run: bool = False,
               verbose: bool = False) -> None:
        if dry_run:
            id = '1'
        else:
            task.cmd.function = None
            id = self.send('submit', task)
        task.id = id

    def cancel(self, task: Task) -> None:
        self.send('cancel', task.id)

    def hold(self, task: Task) -> None:
        self.send('hold', task.id)

    def release_hold(self, task: Task) -> None:
        self.send('release', task.id)

    def get_ids(self) -> set[str]:
        ids = self.send('list')
        return ids

    def send(self, *args: Any) -> Any:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('127.0.0.1', self.port))
            except ConnectionRefusedError:
                raise ConnectionRefusedError(
                    'Local scheduler not responding.  '
                    'Please start it with: "python3 -m myqueue.local"')
            b = pickle.dumps(args)
            assert len(b) < 4096
            s.sendall(b)
            if args[0] == 'stop':
                return
            b = b''.join(iter(partial(s.recv, 4096), b''))
        status, result = pickle.loads(b)
        if status != 'ok':
            raise LocalSchedulerError(status)
        return result

    def get_config(self, queue: str = '') -> tuple[list[tuple[str, int, str]],
                                                   list[str]]:
        return [], []


class Server:
    """Run tasks in subprocesses."""
    def __init__(self,
                 config: Configuration,
                 cores: int = 1,
                 port: int = 39999) -> None:
        self.config = config
        self.port = port

        with Queue(config) as queue:
            queue._read()
            self.next_id = 1 + max((task.int_id for task in queue.tasks),
                                   default=0)

        self.tasks: dict[str, Task] = {}
        self.processes: dict[str, asyncio.subprocess.Process] = {}
        self.aiotasks: dict[str, asyncio.Task] = {}
        self.folder = self.config.home / '.myqueue'

    def start(self) -> None:
        """Start server and wait for cammands."""
        try:
            asyncio.run(self._start())
        except asyncio.exceptions.CancelledError:
            pass

    async def _start(self) -> None:
        for _ in range(5):
            try:
                self.server = await asyncio.start_server(
                    self.recv, '127.0.0.1', self.port)
            except OSError:
                self.port -= 1
            else:
                break
        else:  # no break
            raise OSError('Could not find unused port!')

        print('Port:', self.port)

        async with self.server:  # type: ignore
            await self.server.serve_forever()
            await self.server.wait_closed()

    async def recv(self, reader: Any, writer: Any) -> None:
        """Recieve command from client."""
        data = await reader.read(4096)
        cmd, *args = pickle.loads(data)
        print('COMMAND:', cmd, *args)
        result: Any
        if cmd == 'stop':
            for aiotask in self.aiotasks.values():
                await aiotask
            self.server.close()
            print('BYE')
            return
            result = None
        elif cmd == 'submit':
            task = args[0]
            task.id = str(self.next_id)
            task.state = State.queued
            if all(t.id in self.tasks for t in task.dtasks):
                task.deps = [t.dname for t in task.dtasks]
                self.tasks[task.id] = task
            self.next_id += 1
            result = task.id
        elif cmd == 'list':
            result = list(self.tasks)
        elif cmd == 'cancel':
            id = args[0]
            if id in self.processes:
                self.terminate(id)
            elif id in self.tasks:
                task = self.tasks[id]
                task.state = State.CANCELED
                task.cancel_dependents(list(self.tasks.values()))
                self.tasks = {id: task for id, task in self.tasks.items()
                              if task.state != State.CANCELED}
            result = None
        else:
            1 / 0
        writer.write(pickle.dumps(('ok', result)))
        await writer.drain()
        writer.close()
        self.kick()
        print('JOBS:', list(self.tasks))

    def kick(self) -> None:
        """Check if a new task should be started."""
        self.aiotasks = {id: aiotask
                         for id, aiotask in self.aiotasks.items()
                         if not aiotask.done()}

        for task in self.tasks.values():
            if task.state == State.running:
                return

        for task in self.tasks.values():
            if task.state == State.queued and not task.deps:
                break
        else:  # no break
            return

        print('START', task.id)
        aiotask = asyncio.create_task(self.run(task))
        self.aiotasks[task.id] = aiotask
        # aiotask.add_done_callback(lambda t: self.aiotasks.pop(task.id))

    async def run(self, task: Task) -> None:
        """Run a task."""
        out = f'{task.cmd.short_name}.{task.id}.out'
        err = f'{task.cmd.short_name}.{task.id}.err'

        cmd = str(task.cmd)
        if task.resources.processes > 1:
            mpiexec = f'{self.config.mpiexec} -x OMP_NUM_THREADS=1 '
            mpiexec += f'-np {task.resources.processes} '
            cmd = mpiexec + cmd.replace('python3',
                                        self.config.parallel_python)
        cmd = f'{cmd} 2> {err} > {out}'

        proc = await asyncio.create_subprocess_shell(
            cmd, cwd=task.folder)

        self.processes[task.id] = proc

        loop = asyncio.get_event_loop()
        tmax = task.resources.tmax
        handle = loop.call_later(tmax, self.terminate, task.id)
        task.state = State.running
        (self.folder / f'local-{task.id}-0').write_text('')  # running

        await proc.wait()
        print('END', task.id, proc.returncode)
        handle.cancel()

        del self.tasks[task.id]
        del self.processes[task.id]

        if proc.returncode == 0:
            for t in self.tasks.values():
                if task.dname in t.deps:
                    t.deps.remove(task.dname)
            state = 1
        else:
            if task.state == 'TIMEOUT':
                state = 3
            else:
                state = 2
            task.cancel_dependents(list(self.tasks.values()))
            self.tasks = {id: task for id, task in self.tasks.items()
                          if task.state != 'CANCELED'}

        (self.folder / f'local-{task.id}-{state}').write_text('')

        self.kick()

    def terminate(self, id: str, state: State = State.TIMEOUT) -> None:
        """Terminate a task."""
        print('Terminate', id)
        proc = self.processes.get(id)
        if proc and proc.returncode is None:
            proc.terminate()
            self.tasks[id].state = state


if __name__ == '__main__':
    asyncio.run(Server(Configuration.read())._start())
