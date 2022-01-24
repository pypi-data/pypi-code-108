"""Queue class for interacting with the queue.

File format versions:

5) Changed from mod:func to mod@func.
6) Relative paths.
8) Type of Task.id changed from int to str.

"""
from __future__ import annotations
import json
import time
from collections import defaultdict
from typing import Sequence
from types import TracebackType

from myqueue.config import Configuration
from myqueue.scheduler import get_scheduler, Scheduler
from myqueue.resources import Resources
from myqueue.run import run_tasks
from myqueue.selection import Selection
from myqueue.task import Task
from myqueue.utils import Lock, plural
from myqueue.states import State
from myqueue.email import send_notification, configure_email
from myqueue.pretty import pprint
from myqueue.submitting import submit_tasks


class Queue(Lock):
    """Object for interacting with the scheduler."""
    def __init__(self,
                 config: Configuration,
                 verbosity: int = 1,
                 need_lock: bool = True,
                 dry_run: bool = False):
        self.verbosity = verbosity
        self.need_lock = need_lock
        self.dry_run = dry_run
        self.config = config

        self.folder = config.home / '.myqueue'
        self.fname = self.folder / 'queue.json'

        Lock.__init__(self, self.fname.with_name('queue.json.lock'),
                      timeout=10.0)

        self._scheduler: Scheduler | None = None
        self.tasks: list[Task] = []
        self.changed: set[Task] = set()

    @property
    def scheduler(self) -> Scheduler:
        """Scheduler object."""
        if self._scheduler is None:
            self._scheduler = get_scheduler(self.config)
        return self._scheduler

    def __enter__(self) -> 'Queue':
        if self.dry_run:
            return self
        if self.need_lock:
            self.acquire()
        else:
            try:
                self.acquire()
            except PermissionError:
                pass
        return self

    def __exit__(self,
                 type: Exception,
                 value: Exception,
                 tb: TracebackType) -> None:
        if self.changed and not self.dry_run:
            self._write()
        self.release()

    def list_(self,
              selection: Selection,
              columns: str,
              sort: str | None = None,
              reverse: bool = False,
              short: bool = False,
              use_log_file: bool = False) -> list[Task]:
        """Pretty-print list of tasks."""
        self._read(use_log_file)
        tasks = selection.select(self.tasks)
        if isinstance(sort, str):
            tasks.sort(key=lambda task: task.order(sort),  # type: ignore
                       reverse=reverse)
        pprint(tasks, self.verbosity, columns, short)
        return tasks

    def submit(self,
               tasks: Sequence[Task],
               force: bool = False,
               max_tasks: int = 1_000_000_000,
               read: bool = True) -> None:
        """Submit tasks to queue.

        Parameters
        ==========
        force: bool
            Ignore and remove name.FAILED files.
        """

        if read:
            self._read()

        current = {task.dname: task for task in self.tasks}

        submitted, skipped, ex = submit_tasks(
            self.scheduler, tasks, current,
            force, max_tasks,
            self.verbosity, self.dry_run)

        if ex:
            print()
            print('Skipped', plural(len(skipped), 'task'))

        pprint(submitted, 0, 'ifnaIr',
               maxlines=10 if self.verbosity < 2 else 99999999999999)
        if submitted:
            if self.dry_run:
                print(plural(len(submitted), 'task'), 'to submit')
            else:
                print(plural(len(submitted), 'task'), 'submitted')

        for task in submitted:
            if task.workflow:
                oldtask = current.get(task.dname)
                if oldtask:
                    self.tasks.remove(oldtask)

        self.tasks += submitted
        self.changed.update(submitted)

        if ex:
            raise ex

    def run(self,
            tasks: list[Task]) -> None:
        """Run tasks locally."""
        self._read()
        dnames = {task.dname for task in tasks}
        self._remove([task for task in self.tasks if task.dname in dnames])
        if self.dry_run:
            for task in tasks:
                print(f'{task.folder}: {task.cmd}')
        else:
            run_tasks(tasks)

    def remove(self, selection: Selection) -> None:
        """Remove or cancel tasks."""

        self._read()

        tasks = selection.select(self.tasks)
        tasks = self.find_depending(tasks)

        self._remove(tasks)

    def _remove(self, tasks: list[Task]) -> None:
        t = time.time()
        for task in tasks:
            if task.tstop is None:
                task.tstop = t  # XXX is this for dry_run only?

        if self.dry_run:
            if tasks:
                pprint(tasks, 0)
                print(plural(len(tasks), 'task'), 'to be removed')
        else:
            if self.verbosity > 0:
                if tasks:
                    pprint(tasks, 0)
                    print(plural(len(tasks), 'task'), 'removed')
            for task in tasks:
                if task.state in ['running', 'hold', 'queued']:
                    self.scheduler.cancel(task)
                self.tasks.remove(task)
                # XXX why cancel?
                task.cancel_dependents(self.tasks, time.time())
                self.changed.add(task)

    def sync(self) -> None:
        """Syncronize queue with the real world."""
        self._read()
        in_the_queue = {'running', 'hold', 'queued'}
        ids = self.scheduler.get_ids()
        cancel = []
        remove = []
        for task in self.tasks:
            if task.id not in ids:
                if task.state in in_the_queue:
                    cancel.append(task)
                if not task.folder.is_dir():
                    remove.append(task)

        if cancel:
            if self.dry_run:
                print(plural(len(cancel), 'job'), 'to be canceled')
            else:
                for task in cancel:
                    task.state = State.CANCELED
                    self.changed.add(task)
                print(plural(len(cancel), 'job'), 'canceled')

        if remove:
            if self.dry_run:
                print(plural(len(remove), 'job'), 'to be removed')
            else:
                for task in remove:
                    self.tasks.remove(task)
                    self.changed.add(task)
                print(plural(len(remove), 'job'), 'removed')

    def find_depending(self, tasks: list[Task]) -> list[Task]:
        """Generate list of tasks including dependencies."""
        map = {task.dname: task for task in self.tasks}
        d: dict[Task, list[Task]] = defaultdict(list)
        for task in self.tasks:
            for dname in task.deps:
                tsk = map.get(dname)
                if tsk:
                    d[tsk].append(task)

        removed = []

        def remove(task: Task) -> None:
            removed.append(task)
            for j in d[task]:
                remove(j)

        for task in tasks:
            remove(task)

        return sorted(set(removed), key=lambda task: task.id)

    def modify(self,
               selection: Selection,
               newstate: State,
               email: set[State]) -> None:
        """Modify task(s)."""
        self._read()
        tasks = selection.select(self.tasks)

        if email != {State.undefined}:
            configure_email(self.config)
            for task in tasks:
                if self.dry_run:
                    print(task, email)
                else:
                    task.notifications = ''.join(state.value
                                                 for state in email)
                    self.changed.add(task)

        if newstate != State.undefined:
            for task in tasks:
                if task.state == 'hold' and newstate == 'queued':
                    if self.dry_run:
                        print('Release:', task)
                    else:
                        self.scheduler.release_hold(task)
                elif task.state == 'queued' and newstate == 'hold':
                    if self.dry_run:
                        print('Hold:', task)
                    else:
                        self.scheduler.hold(task)
                elif task.state == 'FAILED' and newstate in ['MEMORY',
                                                             'TIMEOUT']:
                    if self.dry_run:
                        print('FAILED ->', newstate, task)
                    else:
                        task.state = newstate
                        self.changed.add(task)
                else:
                    raise ValueError(f'Can\'t do {task.state} -> {newstate}!')
                print(f'{task.state} -> {newstate}: {task}')
                task.state = newstate
                self.changed.add(task)

    def resubmit(self,
                 selection: Selection,
                 resources: Resources | None) -> None:
        """Resubmit failed or timed-out tasks."""
        self._read()
        tasks = []
        for task in selection.select(self.tasks):
            if task.state not in {'queued', 'hold', 'running'}:
                self.tasks.remove(task)
            task.remove_state_file()
            self.changed.add(task)
            task = Task(task.cmd,
                        deps=task.deps,
                        resources=resources or task.resources,
                        folder=task.folder,
                        restart=task.restart,
                        workflow=task.workflow,
                        creates=task.creates,
                        diskspace=0)
            tasks.append(task)
        self.submit(tasks, read=False)

    def _read(self, use_log_file: bool = False) -> None:
        if use_log_file:
            logfile = self.folder / 'log.csv'
            if logfile.is_file():
                import csv
                with logfile.open() as fd:
                    reader = csv.reader(fd)
                    next(reader)  # skip header
                    self.tasks = [Task.fromcsv(row) for row in reader]
            return

        if self.fname.is_file():
            data = json.loads(self.fname.read_text())
            root = self.folder.parent
            for dct in data['tasks']:
                task = Task.fromdict(dct, root)
                self.tasks.append(task)

        if self.locked:
            self.read_change_files()
            self.check()

    def read_change_files(self) -> None:
        paths = list(self.folder.glob('*-*-*'))
        files = []
        for path in paths:
            _, id, state = path.name.split('-')
            files.append((path.stat().st_ctime, id, state))
            path.unlink()
        states = {'0': State.running,
                  '1': State.done,
                  '2': State.FAILED,
                  '3': State.TIMEOUT}
        for t, id, state in sorted(files):
            self.update(id, states[state], t)

    def update(self,
               id: str,
               state: State,
               t: float = 0.0) -> None:

        for task in self.tasks:
            if task.id == id:
                break
        else:
            print(f'No such task: {id}, {state}')
            return

        t = t or time.time()

        task.state = state

        if state == 'done':
            for tsk in self.tasks:
                if task.dname in tsk.deps:
                    tsk.deps.remove(task.dname)
            task.write_state_file()
            task.tstop = t

        elif state == 'running':
            task.trunning = t

        elif state in ['FAILED', 'TIMEOUT', 'MEMORY']:
            task.cancel_dependents(self.tasks, t)
            task.tstop = t
            task.write_state_file()

        else:
            raise ValueError(f'Bad state: {state}')

        if state != 'running':
            mem = self.scheduler.maxrss(id)
            task.memory_usage = mem

        self.changed.add(task)

    def check(self) -> None:
        t = time.time()

        for task in self.tasks:
            if task.state == 'running':
                delta = t - task.trunning - task.resources.tmax
                if delta > 0:
                    if self.scheduler.has_timed_out(task) or delta > 1800:
                        task.state = State.TIMEOUT
                        task.tstop = t
                        task.cancel_dependents(self.tasks, t)
                        self.changed.add(task)

        bad = {task.dname for task in self.tasks if task.state.is_bad()}
        for task in self.tasks:
            if task.state == 'queued':
                for dep in task.deps:
                    if dep in bad:
                        task.state = State.CANCELED
                        task.tstop = t
                        self.changed.add(task)
                        break

        for task in self.tasks:
            if task.state == 'FAILED':
                if not task.error:
                    oom = task.read_error(self.scheduler)
                    if oom:
                        task.state = State.MEMORY
                        task.write_state_file()
                    self.changed.add(task)

    def kick(self) -> dict[str, int]:
        """Kick the system.

        * Send email notifications
        * restart timed-out tasks
        * restart out-of-memory tasks
        * release/hold tasks to stay under *maximum_diskspace*
        """
        self._read()

        result = {}

        ndct = self.config.notifications
        if ndct:
            notifications = send_notification(self.tasks, **ndct)
            self.changed.update(task for task, statename in notifications)
            result['notifications'] = len(notifications)

        tasks = []
        for task in self.tasks:
            if task.state in ['TIMEOUT', 'MEMORY'] and task.restart:
                nodes = self.config.nodes or [('', {'cores': 1})]
                if not self.dry_run:
                    task.resources = task.resources.bigger(task.state, nodes)
                    task.restart -= 1
                tasks.append(task)
        if tasks:
            tasks = self.find_depending(tasks)
            if self.dry_run:
                pprint(tasks)
            else:
                if self.verbosity > 0:
                    print('Restarting', plural(len(tasks), 'task'))
                for task in tasks:
                    self.tasks.remove(task)
                    task.error = ''
                    task.id = '0'
                    task.state = State.undefined
                self.submit(tasks, read=False)
            result['restarts'] = len(tasks)

        result.update(self.hold_or_release())

        return result

    def hold_or_release(self) -> dict[str, int]:
        maxmem = self.config.maximum_diskspace
        mem = 0
        for task in self.tasks:
            if task.state in {'queued', 'running',
                              'FAILED', 'TIMEOUT', 'MEMORY'}:
                mem += task.diskspace

        held = 0
        released = 0

        if mem > maxmem:
            for task in self.tasks:
                if task.state == 'queued':
                    if task.diskspace > 0:
                        self.scheduler.hold(task)
                        held += 1
                        task.state = State.hold
                        self.changed.add(task)
                        mem -= task.diskspace
                        if mem < maxmem:
                            break
        elif mem < maxmem:
            for task in self.tasks[::-1]:
                if task.state == 'hold' and task.diskspace > 0:
                    self.scheduler.release_hold(task)
                    released += 1
                    task.state = State.queued
                    self.changed.add(task)
                    mem += task.diskspace
                    if mem > maxmem:
                        break

        return {name: n
                for name, n in [('held', held), ('released', released)]
                if n > 0}

    def _write(self) -> None:
        root = self.folder.parent
        dicts = []
        for task in self.tasks:
            dicts.append(task.todict(root))
        text = json.dumps(
            {'version': 8,
             'warning': 'Do NOT edit this file!',
             'unless': 'you know what you are doing.',
             'tasks': dicts},
            indent=2)
        self.fname.write_text(text)

        # Write to log:
        logfile = root / '.myqueue/log.csv'
        write_header = not logfile.is_file()
        with logfile.open('a') as fd:
            for task in self.changed:
                task.tocsv(fd, write_header)
                write_header = False
