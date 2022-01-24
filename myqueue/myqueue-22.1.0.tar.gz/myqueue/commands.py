"""Definitions of commands.

There is a Command base class and five concrete classes:
ShellCommand, ShellScript, PythonScript, PythonModule and
PythonFunction.  Use the factory function command() to create
command objects.
"""
from __future__ import annotations
from typing import Any, Type, Callable
from pathlib import Path
from shlex import quote

from .resources import Resources


class Command:
    """Base class."""
    def __init__(self, name: str, args: list[str]):
        self.args = args
        if args:
            name += '+' + '_'.join(self.args)
        self.name = name
        self.dct: dict[str, Any] = {'args': args}
        self.short_name: str
        self.function: Callable[[], Any] | None = None

    def set_non_standard_name(self, name: str) -> None:
        self.name = name
        self.dct['name'] = name

    def todict(self) -> dict[str, Any]:
        raise NotImplementedError

    @property
    def fname(self) -> str:
        return self.name.replace('/', '\\')  # filename can't contain slashes

    def read_resources(self, path: Path) -> Resources | None:
        """Look for "# MQ: resources=..." comments in script."""
        return None

    def run(self) -> Any:
        import subprocess
        subprocess.run(str(self), shell=True, check=True)
        return None

    def quoted_args(self) -> list[str]:
        return [quote(arg) for arg in self.args]


def create_command(cmd: str,
                   args: list[str] = [],
                   type: str = None,
                   name: str = '') -> Command:
    """Create command object."""
    cmd, _, args2 = cmd.partition(' ')
    if args2:
        args = args2.split() + args
    path, sep, cmd = cmd.rpartition('/')
    if '+' in cmd:
        cmd, _, rest = cmd.rpartition('+')
        args = rest.split('_') + args
    cmd = path + sep + cmd

    cls: Type[Command]
    if type is None:
        if cmd.startswith('shell:'):
            cls = ShellCommand
        elif cmd.endswith('.py'):
            cls = PythonScript
        elif cmd.startswith('workflow:'):
            cls = WorkflowTask
        elif '.py@' in cmd:
            cls = PythonFunctionInScript
        elif '@' in cmd:
            cls = PythonFunction
        elif path:
            cls = ShellScript
        else:
            cls = PythonModule
    else:
        cls = globals()[type.title().replace('-', '')]

    command = cls(cmd, args)

    if name:
        command.set_non_standard_name(name)

    return command


class ShellCommand(Command):
    def __init__(self, cmd: str, args: list[str]):
        Command.__init__(self, cmd, args)
        self.cmd = cmd
        self.short_name = cmd

    def __str__(self) -> str:
        return ' '.join([self.cmd[6:]] + self.quoted_args())

    def todict(self) -> dict[str, Any]:
        return {**self.dct,
                'type': 'shell-command',
                'cmd': self.cmd}


class ShellScript(Command):
    def __init__(self, cmd: str, args: list[str]):
        Command.__init__(self, Path(cmd).name, args)
        self.cmd = cmd
        self.short_name = cmd

    def __str__(self) -> str:
        return ' '.join(['sh', self.cmd] + self.quoted_args())

    def todict(self) -> dict[str, Any]:
        return {**self.dct,
                'type': 'shell-script',
                'cmd': self.cmd}

    def read_resources(self, path: Path) -> Resources | None:
        for line in Path(self.cmd).read_text().splitlines():
            if line.startswith('# MQ: resources='):
                return Resources.from_string(line.split('=', 1)[1])
        return None


class PythonScript(Command):
    def __init__(self, script: str, args: list[str]):
        path = Path(script)
        Command.__init__(self, path.name, args)
        if '/' in script:
            self.script = str(path.absolute())
        else:
            self.script = script
        self.short_name = path.name

    def __str__(self) -> str:
        return 'python3 ' + ' '.join([self.script] + self.quoted_args())

    def todict(self) -> dict[str, Any]:
        return {**self.dct,
                'type': 'python-script',
                'cmd': self.script}

    def read_resources(self, path: Path) -> Resources | None:
        script = Path(self.script)
        if not script.is_absolute():
            script = path / script
        for line in script.read_text().splitlines():
            if line.startswith('# MQ: resources='):
                return Resources.from_string(line.split('=', 1)[1])
        return None


class WorkflowTask(Command):
    def __init__(self,
                 cmd: str,
                 args: list[str],
                 function: Callable[[], Any] = None):
        script, name = cmd.split(':')
        self.script = Path(script)
        Command.__init__(self, name, args)
        self.function = function
        self.short_name = name

    def __str__(self) -> str:
        code = '; '.join(
            ['from myqueue.workflow import run_workflow_function',
             f'run_workflow_function({str(self.script)!r}, {self.name!r})'])
        return f'python3 -c "{code}"'

    def run(self) -> Any:
        assert self.function is not None
        return self.function()

    def todict(self) -> dict[str, Any]:
        return {**self.dct,
                'type': 'workflow-task',
                'cmd': f'{self.script}:{self.name}'}


class PythonModule(Command):
    def __init__(self, mod: str, args: list[str]):
        Command.__init__(self, mod, args)
        self.mod = mod
        self.short_name = mod

    def __str__(self) -> str:
        return ' '.join(['python3', '-m', self.mod] + self.quoted_args())

    def todict(self) -> dict[str, Any]:
        return {**self.dct,
                'type': 'python-module',
                'cmd': self.mod}


class PythonFunction(Command):
    def __init__(self, cmd: str, args: list[str]):
        if ':' in cmd:
            # Backwards compatibility with version 4:
            self.mod, self.func = cmd.rsplit(':', 1)
        else:
            self.mod, self.func = cmd.rsplit('@', 1)
        Command.__init__(self, cmd, args)
        self.short_name = cmd

    def __str__(self) -> str:
        args = ', '.join(repr(convert(arg)) for arg in self.args)
        mod = self.mod
        return f'python3 -c "import {mod}; {mod}.{self.func}({args})"'

    def todict(self) -> dict[str, Any]:
        return {**self.dct,
                'type': 'python-function',
                'cmd': self.mod + '@' + self.func}


class PythonFunctionInScript(Command):
    def __init__(self, cmd: str, args: list[str]):
        script, self.func = cmd.rsplit('@', 1)
        path = Path(script)
        Command.__init__(self, path.name, args)
        if '/' in script:
            self.script = str(path.absolute())
        else:
            self.script = script
        self.short_name = path.name

    def __str__(self) -> str:
        args = ', '.join(repr(convert(arg)) for arg in self.args)
        return (f'python3 -c "import runpy; '
                f'mod = runpy({self.script!r}); '
                f'mod.{self.func}({args})')

    def todict(self) -> dict[str, Any]:
        return {**self.dct,
                'type': 'python-function-in-script',
                'cmd': self.script + '@' + self.func}


def convert(x: str) -> bool | int | float | str:
    """Convert str to bool, int, float or str."""
    if x == 'True':
        return True
    if x == 'False':
        return False
    try:
        f = float(x)
    except ValueError:
        return x
    if int(f) == f:
        return int(f)
    return f
