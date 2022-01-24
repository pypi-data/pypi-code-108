"""User configuration (handling of .myqueue/config.py files)."""
from __future__ import annotations
import subprocess
import warnings
from math import inf
from pathlib import Path
from typing import Any


class Configuration:
    def __init__(self,
                 scheduler: str,
                 nodes: list[tuple[str, dict[str, Any]]] = None,
                 parallel_python: str = 'python3',
                 mpiexec: str = 'mpiexec',
                 extra_args: list[str] = None,
                 maximum_diskspace: float = inf,
                 notifications: dict[str, str] = None,
                 home: Path = None):
        """Configuration object.

        """
        self.scheduler = scheduler
        self.nodes = nodes or []
        self.parallel_python = parallel_python
        self.mpiexec = mpiexec
        self.extra_args = extra_args or []
        self.maximum_diskspace = maximum_diskspace
        self.notifications = notifications or {}
        self.home = home or Path.cwd()

    def __repr__(self) -> str:
        args = ', '.join(f'{name.lstrip("_")}={getattr(self, name)!r}'
                         for name in self.__dict__)
        return f'Configuration({args})'

    def __str__(self) -> str:
        lines = []
        for key, value in self.__dict__.items():
            if key == 'nodes':
                lines.append('nodes')
                n = max((len(name) for name, _ in value), default=0)
                for name, dct in value:
                    lines.append(f'  {name:<{n}}  {dct}')
                continue
            lines.append(f'{key:18} {value}')
        return '\n'.join(lines)

    @classmethod
    def read(self, start: Path = None) -> 'Configuration':
        """Find nearest .myqueue/config.py and read it."""
        if start is None:
            start = Path.cwd()
        home = find_home_folder(start)
        config_file = home / '.myqueue' / 'config.py'
        dct: dict[str, dict[str, Any]] = {}
        exec(compile(config_file.read_text(), str(config_file), 'exec'), dct)
        cfg = dct['config']
        if 'scheduler' not in cfg:
            raise ValueError(
                'Please specify type of scheduler in your '
                f'{home}/.myqueue/config.py '
                "file (must be 'slurm', 'lfs', 'pbs' or 'test').  See "
                'https://myqueue.rtfd.io/en/latest/configuration.html')

        if 'mpi' in cfg or 'mpi_implementation' in cfg:
            warnings.warn(
                'The "mpi" and "mpi_implementation" keywords have been '
                f'deprecated. Please remove them from {config_file}')
            cfg.pop('mpi', None)
            cfg.pop('mpi_implementation', None)

        config = Configuration(**cfg, home=home)
        return config


def find_home_folder(start: Path) -> Path:
    """Find closest .myqueue/ folder."""
    f = start
    while True:
        dir = f / '.myqueue'
        if dir.is_dir():
            return f.absolute().resolve()
        newf = f.parent
        if newf == f:
            break
        f = newf
    raise ValueError('Could not find .myqueue/ folder!')


def guess_scheduler() -> str:
    """Try different scheduler commands to guess the correct scheduler."""
    scheduler_commands = {'sbatch': 'slurm',
                          'bsub': 'lsf',
                          'qsub': 'pbs'}
    commands = []
    for command in scheduler_commands:
        if subprocess.run(['which', command],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0:
            commands.append(command)
    if commands:
        if len(commands) > 1:
            raise ValueError('Please specify a scheduler: ' +
                             ', '.join(scheduler_commands[cmd]
                                       for cmd in commands))
        scheduler = scheduler_commands[commands[0]]
    else:
        scheduler = 'local'
    return scheduler


def guess_configuration(scheduler_name: str = '',
                        queue_name: str = '',
                        in_place: bool = False) -> None:
    """Simple auto-config tool.

    Creates a config.py file.
    """
    from .scheduler import get_scheduler
    from .utils import str2number, mqhome

    folder = mqhome() / '.myqueue'
    if not folder.is_dir():
        folder.mkdir()

    name = scheduler_name or guess_scheduler()
    scheduler = get_scheduler(Configuration(scheduler=name))
    nodelist, extra_args = scheduler.get_config(queue_name)
    nodelist.sort(key=lambda ncm: (-ncm[1], str2number(ncm[2])))
    nodelist2: list[tuple[str, int, str]] = []
    done: set[int] = set()
    for name, cores, memory in nodelist:
        if cores not in done:
            nodelist2.insert(len(done), (name, cores, memory))
            done.add(cores)
        else:
            nodelist2.append((name, cores, memory))

    cfg: dict[str, Any] = {'scheduler': scheduler.name}

    if nodelist2:
        cfg['nodes'] = [(name, {'cores': cores, 'memory': memory})
                        for name, cores, memory in nodelist2]
    if extra_args:
        cfg['extra_args'] = extra_args

    text = f'config = {cfg!r}\n'
    text = text.replace('= {', '= {\n    ')
    text = text.replace(", 'nodes'", ",\n    'nodes'")
    text = text.replace(", 'extra_args'", ",\n    'extra_args'")
    text = text.replace('(', '\n        (')
    text = '# generated with mq config\n' + text

    if in_place:
        cfgfile = folder / 'config.py'
        if cfgfile.is_file():
            cfgfile.rename(cfgfile.with_name('config.py.old'))
        cfgfile.write_text(text)
    else:
        print(text)
