from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Iterator, Sequence
from warnings import warn

from myqueue.commands import Command, WorkflowTask, create_command
from myqueue.resources import Resources, T
from myqueue.states import State

if TYPE_CHECKING:
    from .scheduler import Scheduler

UNSPECIFIED = 'hydelifytskibadut'


class Task:
    """Task object.

    Parameters
    ----------

    cmd: :class:`myqueue.commands.Command`
        Command to be run.
    resources: Resources
        Combination of number of cores, nodename, number of processes
        and maximum time.
    deps: list of Path objects
        Dependencies.
    restart: int
        How many times to restart task.
    workflow: bool
        Task is part of a workflow.
    diskspace: float
        Disk-space used.  See :ref:`max_disk`.
    folder: Path
        Folder where task should run.
    creates: list of str
        Name of files created by task.
    """

    def __init__(self,
                 cmd: Command,
                 resources: Resources,
                 deps: list[Path],
                 restart: int,
                 workflow: bool,
                 diskspace: int,
                 folder: Path,
                 creates: list[str],
                 notifications: str = '',
                 state: State = State.undefined,
                 id: str = '0',
                 error: str = '',
                 memory_usage: int = 0,
                 tqueued: float = 0.0,
                 trunning: float = 0.0,
                 tstop: float = 0.0) -> None:

        self.cmd = cmd
        self.resources = resources
        self.deps = deps
        self.restart = restart
        self.workflow = workflow
        self.diskspace = diskspace
        self.folder = folder
        self.notifications = notifications
        self.creates = creates

        assert isinstance(state, State), state
        self.state = state
        self.id = id
        self.error = error

        # Timing:
        self.tqueued = tqueued
        self.trunning = trunning
        self.tstop = tstop

        self.memory_usage = memory_usage

        self.dname = folder / cmd.name
        self.dtasks: list[Task] = []
        self.activation_script: Path | None = None
        self._done: bool | None = None
        self.result = UNSPECIFIED

    @property
    def name(self) -> str:
        return f'{self.cmd.name}.{self.id}'

    @ property
    def int_id(self) -> int:
        return int(self.id.split('.')[0])

    def running_time(self, t: float = None) -> float:
        if self.state in ['CANCELED', 'queued', 'hold']:
            dt = 0.0
        elif self.state == 'running':
            t = t or time.time()
            dt = t - self.trunning
        else:
            dt = self.tstop - self.trunning
        return dt

    def words(self) -> list[str]:
        t = time.time()
        age = t - self.tqueued
        dt = self.running_time(t)

        info = []
        if self.restart:
            info.append(f'*{self.restart}')
        if self.deps:
            info.append(f'd{len(self.deps)}')
        if self.cmd.args:
            info.append(f'+{len(self.cmd.args)}')
        if self.diskspace:
            info.append('D')
        if self.notifications:
            info.append(self.notifications)

        return [self.id,
                str(self.folder) + '/',
                self.cmd.short_name,
                ' '.join(self.cmd.args),
                ','.join(info),
                str(self.resources),
                seconds_to_time_string(age),
                self.state.name,
                seconds_to_time_string(dt),
                self.error]

    def __str__(self) -> str:
        return ' '.join(self.words())

    def __repr__(self) -> str:
        return str(self.dname)
        dct = self.todict()
        return f'Task({dct!r})'

    def order(self, column: str) -> int | str | Path | float | State:
        """ifnraste"""
        if column == 'i':
            return self.id
        if column == 'f':
            return self.folder
        if column == 'n':
            return self.name
        if column == 'A':
            return len(self.cmd.args)
        if column == 'r':
            return self.resources.cores * self.resources.tmax
        if column == 'a':
            return self.tqueued
        if column == 's':
            return self.state
        if column == 't':
            return self.running_time()
        if column == 'e':
            return self.error
        raise ValueError(f'Unknown column: {column}!  '
                         'Must be one of i, f, n, a, I, r, A, s, t or e')

    def todict(self, root: Path = None) -> dict[str, Any]:
        folder = self.folder
        deps = self.deps
        if root:
            folder = folder.relative_to(root)
            deps = [dep.relative_to(root) for dep in self.deps]
        return {
            'id': self.id,
            'folder': str(folder),
            'cmd': self.cmd.todict(),
            'state': self.state.name,
            'resources': self.resources.todict(),
            'restart': self.restart,
            'workflow': self.workflow,
            'deps': [str(dep) for dep in deps],
            'diskspace': self.diskspace,
            'notifications': self.notifications,
            'creates': self.creates,
            'tqueued': self.tqueued,
            'trunning': self.trunning,
            'tstop': self.tstop,
            'error': self.error}

    def tocsv(self,
              fd: IO[str] = sys.stdout,
              write_header: bool = False) -> None:
        if write_header:
            print('# id,folder,cmd,resources,state,restart,workflow,'
                  'diskspace,deps,creates,tqueued,trunning,tstop,error,momory',
                  file=fd)
        t1, t2, t3 = (datetime.fromtimestamp(t).strftime('"%Y-%m-%d %H:%M:%S"')
                      for t in [self.tqueued, self.trunning, self.tstop])
        deps = ','.join(str(dep) for dep in self.deps)
        creates = ','.join(self.creates)
        error = self.error.replace('"', '""')
        print(f'{self.id},'
              f'"{self.folder}",'
              f'"{self.cmd.name}",'
              f'{self.resources},'
              f'{self.state},'
              f'{self.restart},'
              f'{int(self.workflow)},'
              f'{self.diskspace},'
              f'"{deps}",'
              f'"{creates}",'
              f'{t1},{t2},{t3},'
              f'"{error}",'
              f'{self.memory_usage},'
              f'"{self.notifications}"',
              file=fd)

    @staticmethod
    def fromcsv(row: list[str]) -> Task:
        (id, folder, name, resources, state, restart, workflow, diskspace,
         deps, creates, t1, t2, t3, error) = row[:14]
        try:
            memory_usage = 0 if len(row) == 14 else int(row[14])
        except ValueError:  # read old corrupted log.csv files
            memory_usage = 0
        notifications = '' if len(row) < 16 else row[15]
        return Task(create_command(name),
                    Resources.from_string(resources),
                    [Path(dep) for dep in deps.split(',')],
                    int(restart),
                    bool(workflow),
                    int(diskspace),
                    Path(folder),
                    creates.split(','),
                    notifications,
                    State[state],
                    id,
                    error,
                    memory_usage,
                    *(datetime.strptime(t, '%Y-%m-%d %H:%M:%S').timestamp()
                      for t in (t1, t2, t3)))

    @staticmethod
    def fromdict(dct: dict[str, Any], root: Path) -> Task:
        dct = dct.copy()

        # Backwards compatibility with version 2:
        if 'restart' not in dct:
            dct['restart'] = 0
        else:
            dct['restart'] = int(dct['restart'])
        if 'diskspace' not in dct:
            dct['diskspace'] = 0

        # Backwards compatibility:
        if 'creates' not in dct:
            dct['creates'] = []

        f = dct.pop('folder')
        if f.startswith('/'):
            # Backwards compatibility with version 5:
            folder = Path(f)
            deps = [Path(dep) for dep in dct.pop('deps')]
        else:
            folder = root / f
            deps = [root / dep for dep in dct.pop('deps')]

        id = str(dct.pop('id'))

        return Task(cmd=create_command(**dct.pop('cmd')),
                    resources=Resources(**dct.pop('resources')),
                    state=State[dct.pop('state')],
                    folder=folder,
                    deps=deps,
                    notifications=dct.pop('notifications', ''),
                    id=id,
                    **dct)

    def infolder(self, folder: Path, recursive: bool) -> bool:
        return folder == self.folder or (recursive and
                                         folder in self.folder.parents)

    def read_state_file(self) -> State:
        """Read state file."""
        if (self.folder / f'{self.cmd.fname}.FAILED').is_file():
            return State.FAILED
        if self.creates:
            for pattern in self.creates:
                if not any(self.folder.glob(pattern)):
                    return State.undefined
            return State.done
        if (self.folder / f'{self.cmd.fname}.done').is_file():
            return State.done
        state_file = self.folder / f'{self.cmd.fname}.state'
        try:
            return State[json.loads(state_file.read_text())['state']]
        except (FileNotFoundError, KeyError):
            return State.undefined

    def write_state_file(self) -> None:
        """Write state file for workflows."""
        if not self.workflow:
            return
        if self.state == State.done and isinstance(self.cmd, WorkflowTask):
            # Already done when writing results of function call
            return
        if not self.folder.is_dir():
            return
        state_file = self.folder / f'{self.cmd.fname}.state'
        state_file.write_text(f'{{"state": "{self.state}"}}\n')

    def remove_state_file(self) -> None:
        """Remove state file if it is there."""
        p = self.folder / f'{self.cmd.fname}.state'
        if p.is_file():
            p.unlink()

    def read_error(self, scheduler: 'Scheduler') -> bool:
        """Check error message.

        Return True if out of memory.
        """
        self.error = '-'  # mark as already read

        path = scheduler.error_file(self)

        try:
            lines = path.read_text().splitlines()
        except (FileNotFoundError, UnicodeDecodeError):
            return False

        for line in lines[::-1]:
            ll = line.lower()
            if any(x in ll for x in ['error:', 'memoryerror', 'malloc',
                                     'out of memory']):
                self.error = line
                if line.endswith('memory limit at some point.'):
                    return True
                if 'malloc' in line:
                    return True
                if line.startswith('MemoryError'):
                    return True
                if 'oom-kill' in line:
                    return True
                if line.endswith('out of memory'):
                    return True
                return False

        if lines:
            self.error = lines[-1]
        return False

    def ideps(self, map: dict[Path, Task]) -> Iterator[Task]:
        """Yield task and its dependencies."""
        yield self
        for dname in self.deps:
            yield from map[dname].ideps(map)

    def submit(self, verbosity: int = 1, dry_run: bool = False) -> None:
        """Submit task.

        Parameters
        ----------

        verbosity: int
            Must be 0, 1 or 2.
        dry_run: bool
            Don't actually submit the task.
        """
        from .queue import Queue
        from.config import Configuration
        config = Configuration.read()
        with Queue(config, verbosity, dry_run=dry_run) as queue:
            queue.submit([self])

    def find_dependents(self,
                        tasks: Sequence[Task]) -> Iterator[Task]:
        """Yield dependents."""
        for task in tasks:
            if self.dname in task.deps and self is not task:
                yield task
                yield from task.find_dependents(tasks)

    def cancel_dependents(self,
                          tasks: Sequence[Task],
                          t: float = 0.0) -> int:
        """Cancel dependents."""
        ncancel = 0
        for task in self.find_dependents(tasks):
            task.state = State.CANCELED
            task.tstop = t
            ncancel += 1
        return ncancel

    def run(self) -> None:
        self.result = self.cmd.run()

    def get_venv_activation_line(self) -> str:
        if self.activation_script:
            return (f'source {self.activation_script}\n'
                    f'echo "venv: {self.activation_script}"\n')
        return ''


def task(cmd: str,
         args: list[str] = [],
         *,
         resources: str = '',
         workflow: bool = False,
         name: str = '',
         deps: str | list[str] | Task | list[Task] = '',
         cores: int = 0,
         nodename: str = '',
         processes: int = 0,
         tmax: str = '',
         folder: str = '',
         restart: int = 0,
         diskspace: float = 0.0,
         creates: list[str] = []) -> Task:
    """Create a Task object.

    ::

        task = task('abc.py')

    Parameters
    ----------
    cmd: str
        Command to be run.
    args: list of str
        Command-line arguments or function arguments.
    resources: str
        Resources::

            'cores[:nodename][:processes]:tmax'

        Examples: '48:1d', '32:1h', '8:xeon8:1:30m'.  Can not be used
        togeter with any of "cores", "nodename", "processes" and "tmax".
    name: str
        Name to use for task.  Default is <cmd>[+<arg1>[_<arg2>[_<arg3>]...]].
    deps: str, list of str, Task object  or list of Task objects
        Dependencies.  Examples: "task1,task2", "['task1', 'task2']".
    cores: int
        Number of cores (default is 1).
    nodename: str
        Name of node.
    processes: int
        Number of processes to start (default is one for each core).
    tmax: str
        Maximum time for task.  Examples: "40s", "30m", "20h" and "2d".
    workflow: bool
        Task is part of a workflow.
    folder: str
        Folder where task should run (default is current folder).
    restart: int
        How many times to restart task.
    diskspace: float
        Diskspace used.  See :ref:`max_disk`.
    creates: list of str
        Name of files created by task
        (can be both full filenames or patterns matching filenames).

    Returns
    -------
    Task
        Object representing the task.
    """

    path = Path(folder).absolute()

    dpaths = []
    if deps:
        if isinstance(deps, str):
            deps = deps.split(',')
        elif isinstance(deps, Task):
            deps = [deps]
        for dep in deps:
            if isinstance(dep, str):
                p = path / dep
                if '..' in p.parts:
                    p = p.parent.resolve() / p.name
                dpaths.append(p)
            else:
                dpaths.append(dep.dname)

    if '@' in cmd:
        # Old way of specifying resources:
        c, r = cmd.rsplit('@', 1)
        if r[0].isdigit():
            cmd = c
            resources = r
            warn(f'Please use resources={r!r} instead of deprecated '
                 f'...@{r} syntax!')

    command = create_command(cmd, args, name=name)

    res: Resources | None = None

    if cores == 0 and nodename == '' and processes == 0 and tmax == '':
        if resources:
            res = Resources.from_string(resources)
        else:
            res = command.read_resources(path)
    else:
        assert resources == ''

    if res is None:
        res = Resources(cores, nodename, processes, T(tmax or '10m'))

    return Task(command,
                res,
                dpaths,
                restart,
                workflow,
                int(diskspace),
                path,
                creates)


def seconds_to_time_string(n: float) -> str:
    """Convert number of seconds to string.

    >>> seconds_to_time_string(10)
    '0:10'
    >>> seconds_to_time_string(3601)
    '1:00:01'
    >>> seconds_to_time_string(24 * 3600)
    '1:00:00:00'
    """
    n = int(n)
    d, n = divmod(n, 24 * 3600)
    h, n = divmod(n, 3600)
    m, s = divmod(n, 60)
    if d:
        return f'{d}:{h:02}:{m:02}:{s:02}'
    if h:
        return f'{h}:{m:02}:{s:02}'
    return f'{m}:{s:02}'
