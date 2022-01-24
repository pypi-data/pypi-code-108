from __future__ import annotations
import ast
import runpy
from functools import partial
from pathlib import Path
from typing import Any, Callable, Type, Sequence, Union
from types import TracebackType


from myqueue.caching import CachedFunction, create_cached_function
from myqueue.commands import (Command, PythonModule, PythonScript,
                              ShellCommand, ShellScript, WorkflowTask)
from myqueue.resources import Resources
from myqueue.states import State

from .progress import progress_bar
from .task import UNSPECIFIED, Task
from .utils import chdir, plural
from argparse import Namespace

DEFAULT_VERBOSITY = 1


def workflow(args: Namespace,
             folders: list[Path],
             verbosity: int = DEFAULT_VERBOSITY) -> list[Task]:
    """Collect tasks from workflow script(s) and folders."""
    if args.arguments:
        kwargs = str2kwargs(args.arguments)
    else:
        kwargs = {}

    if args.pattern:
        pattern = args.script
        tasks = workflow_from_scripts(pattern,
                                      kwargs,
                                      folders,
                                      verbosity=verbosity)
    else:
        tasks = workflow_from_script(Path(args.script),
                                     kwargs,
                                     folders,
                                     verbosity=verbosity)

    if args.targets:
        names = args.targets.split(',')
        tasks = filter_tasks(tasks, names)

    return tasks


WorkflowFunction = Callable[[], None]


def get_workflow_function(path: Path,
                          kwargs: dict[str, Any] = {}) -> WorkflowFunction:
    """Get workflow function from script."""
    module = runpy.run_path(str(path))  # type: ignore # bug in typeshed?
    try:
        func = module['workflow']
    except KeyError:
        func = module['create_tasks']
    if kwargs:
        name = func.__name__
        func = partial(func, **kwargs)
        func.__name__ = name
    return func


def workflow_from_scripts(
        pattern: str,
        kwargs: dict[str, Any],
        folders: list[Path],
        verbosity: int = DEFAULT_VERBOSITY) -> list[Task]:
    """Generate tasks from workflows defined by '**/*{script}'."""
    tasks: list[Task] = []
    paths = [path
             for folder in folders
             for path in folder.glob('**/*' + pattern)]
    pb = progress_bar(len(paths),
                      f'Scanning {len(paths)} scripts:',
                      verbosity)

    for path in paths:
        func = get_workflow_function(path, kwargs)
        tasks += get_tasks_from_folder(path.parent, func, path.absolute())
        next(pb)
    return tasks


def workflow_from_script(script: Path,
                         kwargs: dict[str, Any],
                         folders: list[Path],
                         verbosity: int = DEFAULT_VERBOSITY) -> list[Task]:
    """Collect tasks from workflow defined in python script."""
    func = get_workflow_function(script, kwargs)

    tasks: list[Task] = []

    n_folders = plural(len(folders), 'folder')
    pb = progress_bar(len(folders),
                      f'Scanning {n_folders}:',
                      verbosity)
    for folder in folders:
        tasks += get_tasks_from_folder(folder, func, script.absolute())
        next(pb)

    return tasks


def filter_tasks(tasks: list[Task], names: list[str]) -> list[Task]:
    """Filter tasks that are not in names or in dependencies of names."""
    include = set()
    map = {task.dname: task for task in tasks}
    for task in tasks:
        if task.cmd.name in names:
            for t in task.ideps(map):
                include.add(t)
    filteredtasks = list(include)
    return filteredtasks


def str2kwargs(args: str) -> dict[str, int | str | bool | float]:
    """Convert str to dict.

    >>> str2kwargs('name=hello,n=5')
    {'name': 'hello', 'n': 5}
    """
    kwargs = {}
    for arg in args.split(','):
        key, value = arg.split('=')
        try:
            v = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            v = value
        kwargs[key] = v
    return kwargs


def get_tasks_from_folder(folder: Path,
                          func: Callable,
                          script: Path) -> list[Task]:
    """Collect tasks from folder."""
    with chdir(folder):
        if func.__name__ == 'create_tasks':
            tasks = func()
            for task in tasks:
                task.workflow = True
        else:
            tasks = collect(func, script)

    return tasks


class StopCollecting(Exception):
    """Workflow needs an actual result instead of a dummy Result object."""


class StopRunning(Exception):
    """The correct task has finished running: Stop workflow function."""


class RunHandle:
    """Result of calling run().  Can be used as a context manager."""
    def __init__(self, task: Task, runner: 'Runner'):
        self.task = task
        self.runner = runner

    @property
    def result(self) -> 'Result':
        """Result from Python-function tasks."""
        result = self.task.result
        if result is UNSPECIFIED:
            return Result(self.task)
        assert not isinstance(result, str)
        return result

    @property
    def done(self) -> bool:
        """Has task been successfully finished?"""
        return self.task.state == State.done

    def __enter__(self) -> 'RunHandle':
        self.runner.dependencies.append(self.task)
        return self

    def __exit__(self,
                 exc_type: Type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> None:
        task = self.runner.dependencies.pop()
        assert task is self.task


class Result:
    """Result object for a task - used for finding dependencies."""
    def __init__(self, task: Task):
        self.task = task

    def __getattr__(self, attr: str) -> 'Result':
        return self

    def __lt__(self, other: Any) -> bool:
        raise StopCollecting

    __gt__ = __lt__

    __getitem__ = __getattr__
    __add__ = __getattr__


def get_name(func: Callable) -> str:
    """Give a name to a function.

    >>> import time
    >>> get_name(time.sleep)
    'time.sleep'
    """
    mod = func.__module__
    if mod in ['<run_path>', '__main__']:
        return func.__name__
    return f'{mod}.{func.__name__}'


class ResourceHandler:
    """Resource decorator and context manager."""
    def __init__(self, kwargs: dict[str, Any], runner: 'Runner'):
        self.kwargs = kwargs
        self.runner = runner
        self.old_kwargs: dict

    def __call__(self, workflow_function: Callable[[], Any]
                 ) -> Callable[[], Any]:
        def new() -> Any:
            with self:
                return workflow_function()
        return new

    def __enter__(self) -> None:
        self.old_kwargs = self.runner.resource_kwargs
        self.runner.resource_kwargs = {**self.old_kwargs, **self.kwargs}

    def __exit__(self,
                 exc_type: Type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> None:
        self.runner.resource_kwargs = self.old_kwargs


class Runner:
    """Wrapper for collecting tasks from workflow function."""
    def __init__(self) -> None:
        self.tasks: list[Task] | None = None
        self.dependencies: list[Task] = []
        self.resource_kwargs = {'tmax': '10m',
                                'cores': 1,
                                'nodename': '',
                                'processes': 0,
                                'restart': 0}
        self.target = ''
        self.workflow_script: Path | None = None

    def run(self,
            *,
            function: Union[Callable | CachedFunction] = None,
            script: Union[Path, str] = None,
            module: str = None,
            shell: str = None,
            name: str = '',
            args: Sequence[Any] = [],
            kwargs: dict[str, Any] = {},
            deps: list[RunHandle] = [],
            tmax: str = None,
            cores: int = None,
            nodename: str = None,
            processes: int = None,
            restart: int = None,
            folder: Path | str = '.') -> RunHandle:
        """Run or submit a task.

        The type of task is specifyed by one and only one of the arguments
        `function`, `script`, `module` or `shell`.

        Parameters
        ----------
        function:
            A Python function.
        script:
            Shell-script or Python-script.
        module:
            Name of a Python module.
        shell:
            Shell command.  Must be found in $PATH.
        args: list of objects
            Command-line arguments or function arguments.
        name: str
            Name to use for task.  Default is name of function, script, module
            or shell command.
        deps: list of run handle objects
            Dependencies.
        cores: int
            Number of cores (default is 1).
        nodename: str
            Name of node.
        processes: int
            Number of processes to start (default is one for each core).
        tmax: str
            Maximum time for task.  Examples: "40s", "30m", "20h" and "2d".
        folder: str
            Folder where task should run (default is current folder).
        restart: int
            How many times to restart task.

        Returns
        -------
        RunHandle
            Object representing the run.
        """
        dependencies = self.extract_dependencies(args, kwargs, deps)

        resource_kwargs = {}
        values = [tmax, cores, nodename, processes, restart]
        for value, (key, default) in zip(values,
                                         self.resource_kwargs.items()):
            resource_kwargs[key] = value if value is not None else default

        task = create_task(function,
                           script,
                           module,
                           shell,
                           name,
                           args,
                           kwargs,
                           dependencies,
                           self.workflow_script,
                           Path(folder).absolute(),
                           resource_kwargs.pop('restart'),  # type: ignore
                           **resource_kwargs)

        if self.target:
            if task.cmd.fname == self.target:
                task.run()
                raise StopRunning
        elif self.tasks is not None:
            if task.state != State.done:
                self.tasks.append(task)
        else:
            task.run()

        return RunHandle(task, self)

    def extract_dependencies(self,
                             args: Sequence[Any],
                             kwargs: dict[str, Any],
                             deps: list[RunHandle]) -> list[Path]:
        """Find dependencies on other tasks."""
        tasks = set(self.dependencies)
        for handle in deps:
            tasks.add(handle.task)
        for thing in list(args) + list(kwargs.values()):
            if isinstance(thing, Result):
                tasks.add(thing.task)
        return [task.dname for task in tasks]

    def wrap(self, function: Callable, **run_kwargs: Any) -> Callable:
        """Wrap a function as a task.

        Takes the same keyword arguments as `run`
        (except module, script and shell).

        These two are equivalent::

            result = run(function=func, args=args, kwargs=kwargs, ...).result
            result = wrap(func, ...)(*args, **kwargs)

        """
        def wrapper(*args: Any, **kwargs: Any) -> Result:
            handle = self.run(function=function,
                              args=args,
                              kwargs=kwargs,
                              **run_kwargs)
            return handle.result
        return wrapper

    def resources(self,
                  *,
                  tmax: str = None,
                  cores: int = None,
                  nodename: str = None,
                  processes: int = None,
                  restart: int = None) -> ResourceHandler:
        """Resource decorator and context manager.

        Parameters
        ----------
        cores: int
            Number of cores (default is 1).
        nodename: str
            Name of node.
        processes: int
            Number of processes to start (default is one for each core).
        tmax: str
            Maximum time for task.  Examples: "40s", "30m", "20h" and "2d".
        restart: int
            How many times to restart task.
        """
        keys = ['tmax', 'cores', 'nodename', 'processes', 'restart']
        values = [tmax, cores, nodename, processes, restart]
        kwargs = {key: value
                  for key, value in zip(keys, values)
                  if value is not None}
        return ResourceHandler(kwargs, self)


runner = Runner()
run = runner.run
wrap = runner.wrap
resources = runner.resources


def create_task(function: Callable = None,
                script: Union[Path | str] = None,
                module: str = None,
                shell: str = None,
                name: str = '',
                args: Sequence[Any] = [],
                kwargs: dict[str, Any] = {},
                deps: list[Path] = [],
                workflow_script: Path = None,
                folder: Path = Path('.'),
                restart: int = 0,
                **resource_kwargs: Any) -> Task:
    """Create a Task object."""
    if sum(arg is not None
           for arg in [function, module, script, shell]) != 1:
        1 / 0

    command: Command

    if function:
        name = name or get_name(function)
        cached_function = create_cached_function(function, name, args, kwargs)
        command = WorkflowTask(f'{workflow_script}:{name}', [],
                               cached_function)
    elif module:
        assert not kwargs
        command = PythonModule(module, [str(arg) for arg in args])
    elif script:
        assert not kwargs
        path = folder / script
        assert path.is_file(), path
        if path.suffix == '.py':
            command = PythonScript(str(path), [str(arg) for arg in args])
        else:
            command = ShellScript(str(path), [str(arg) for arg in args])
    else:
        assert not kwargs
        assert isinstance(shell, str)
        command = ShellCommand('shell:' + shell, [str(arg) for arg in args])

    res = Resources.from_args_and_command(command=command,
                                          path=folder,
                                          **resource_kwargs)

    task = Task(command,
                deps=deps,
                resources=res,
                folder=folder,
                restart=restart,
                workflow=True,
                diskspace=0,
                creates=[])

    if function and not any(isinstance(thing, Result)
                            for thing in list(args) + list(kwargs.values())):
        if cached_function.has(*args, **kwargs):
            task.result = cached_function()
            task.state = State.done

    return task


def collect(workflow_function: Callable,
            script: Path) -> list[Task]:
    """Collecting tasks from workflow function."""
    runner.tasks = []
    runner.workflow_script = script
    try:
        workflow_function()
    except StopCollecting:
        pass

    tasks = runner.tasks
    runner.tasks = None
    return tasks


def run_workflow_function(script: str, name: str) -> None:
    """Run specific task in workflow function."""
    workflow_function = get_workflow_function(Path(script))
    runner.target = name
    try:
        workflow_function()
    except StopRunning:
        pass
    runner.target = ''
