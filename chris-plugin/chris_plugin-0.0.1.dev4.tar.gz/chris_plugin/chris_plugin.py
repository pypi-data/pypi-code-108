import argparse
import sys
from pathlib import Path
import functools
from typing import Callable, Optional
from collections import namedtuple
from chris_plugin.main_function import MainFunction, is_plugin_main, is_fs
from chris_plugin._registration import register, PluginDetails
from chris_plugin.types import ChrisPluginType


def _resolve_type(plugin_type: Optional[ChrisPluginType], func: Callable) -> ChrisPluginType:
    try:
        is_plugin_main(func)
    except ValueError as e:
        print(e)
        sys.exit(1)

    inspected_type: ChrisPluginType = 'fs' if is_fs(func) else 'ds'  # type: ignore
    if plugin_type is None:
        return inspected_type
    if plugin_type == 'ts':
        return plugin_type
    if plugin_type != inspected_type:
        print(f'Specified plugin_type="{plugin_type}" but detected "{inspected_type}"')
        print('Please check your main function signature.')
        sys.exit(1)
    return plugin_type


def _mkdir(d: Path):
    if d.exists():
        _check_is_dir(d)
        return
    d.mkdir(parents=True)


def _check_is_dir(d: Path):
    if not d.is_dir():
        print(f'Not a directory: {d}', file=sys.stderr)
        sys.exit(1)


def chris_plugin(
        main: MainFunction = None, /, *,
        parser: Optional[argparse.ArgumentParser] = None,
        plugin_type: Optional[ChrisPluginType] = None,
        category: str = '',
        icon: str = '',
        title: Optional[str] = None,
        min_number_of_workers: int = 1,
        max_number_of_workers: int = 1,
        min_memory_limit: str = '',
        max_memory_limit: str = '',
        min_cpu_limit: str = '',
        max_cpu_limit: str = '',
        min_gpu_limit: int = 0,
        max_gpu_limit: int = 0
):
    """
    Creates a decorator which identifies a *ChRIS* plugin main function
    and associates the *ChRIS* plugin with metadata.

    When called, CLI arguments are parsed and passed to the decorated function
    as its first argument. It is also given the data directories as
    [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path),
    depending on the type of plugin:

    - ["fs"](https://github.com/FNNDSC/chris_plugin/wiki/About-Plugins#fs)
      plugins are given one data directory
    - ["ds"](https://github.com/FNNDSC/chris_plugin/wiki/About-Plugins#ds)
      and ["ts"](https://github.com/FNNDSC/chris_plugin/wiki/About-Plugins#ts)
      plugins are given two data directories

    All data directories are made sure to exist, and the output directory is first
    created if needed.


    Examples
    --------

    *ds* plugin example:

    ```python
    from chris_plugin import chris_plugin

    @chris_plugin(title='Example', min_memory_limit='300Mi')
    def main(options, inputdir, outputdir):
        print('do something')
    ```

    *fs* plugin example with a required argument:

    ```python
    from argparse import ArgumentParser
    from chris_plugin import chris_plugin

    parser = ArgumentParser(description='Creates a file out.txt')
    parser.add_argument('--name', required=True)

    @chris_plugin(parser=parser)
    def main(options, outputdir):
        (outputdir / 'out.txt').write_text(f'hello, {options.name}')
    ```

    At runtime, the function decorated by `@chris_plugin` accepts 0, 2, or 3
    arguments. As a 0-argument function it can be invoked as a typical "main"
    function:

    ```python
    @chris_plugin
    def main(options, outputdir):
        ...

    if __name__ == '__main__':
        main()
    ```

    Importantly, for the program to be a valid *ChRIS* plugin, it must specify
    the decorated function in `console_scripts` of `setup.py`:

    ```python
    from setuptools import setup
    setup(
        ...,
        entry_points={
            'console_scripts': [
                'commandname = app:main'
            ]
        }
    )
    ```

    The decorated function can be invoked from Python with 2 or 3 arguments,
    which makes it possible to test programmatically:

    ```python
    parser = ArgumentParser()
    parser.add_argument('--something', type=float, default=1.5)
    options = parser.parse_args(['--something', '2.2'])

    with tempfile.TemporaryDirectory() as tmpdirname:
        main(options, Path(tmpdirname))  # fs plugin main
    ```

    Parameters
    ----------
    parser : argparse.ArgumentParser
        argument parser
    plugin_type: str
        one of: 'fs', 'ds', 'ts'
    category: str
        category name
    icon: str
        URL of icon
    title: str
        plugin title
    min_number_of_workers: int
        number of workers for multi-node parallelism
    max_number_of_workers: int
        worker request ceiling
    min_memory_limit: str
        minimum memory requirement. Supported units: 'Mi', 'Gi'
    max_memory_limit: str
        memory usage ceiling
    min_cpu_limit: str
        minimum CPU requirement, in millicores.
        e.g. "1000m" is a request for 1 CPU core
    max_cpu_limit: str
        CPU usage ceiling
    min_gpu_limit: int
        minimum number of GPUs the plugin must use.
        0: GPU is disabled. If min_gpu_limit > 1, GPU is enabled.
    max_gpu_limit: int
        maximum number of GPUs the plugin may use

    """
    def wrap(main: MainFunction) -> Callable[[], None]:
        nonlocal parser
        if parser is None:
            parser = argparse.ArgumentParser()

        verified_type = _resolve_type(plugin_type, main)
        if verified_type != 'fs':
            parser.add_argument('inputdir', help='directory containing input files')
        parser.add_argument('outputdir', help='directory containing output files')

        register(PluginDetails(
            parser=parser,
            type=verified_type,
            category=category,
            icon=icon,
            title=title,
            min_number_of_workers=min_number_of_workers,
            max_number_of_workers=max_number_of_workers,
            min_memory_limit=min_memory_limit,
            max_memory_limit=max_memory_limit,
            min_cpu_limit=min_cpu_limit,
            max_cpu_limit=max_cpu_limit,
            min_gpu_limit=min_gpu_limit,
            max_gpu_limit=max_gpu_limit
        ))

        @functools.wraps(main)
        def wrapper(*args):
            if args:
                options, inputdir, outputdir = _call_from_python(args)
            else:
                options, inputdir, outputdir = _call_from_cli(parser)

            if verified_type == 'fs' and inputdir is not None:
                raise ValueError(f'inputdir={inputdir} given to fs-type plugin')

            output_path = Path(outputdir)
            _mkdir(output_path)

            if verified_type == 'fs':
                return main(options, outputdir)

            if inputdir is None:
                raise ValueError('inputdir is None')

            input_path = Path(inputdir)
            _check_is_dir(input_path)
            main(options, input_path, output_path)

        return wrapper

    # See if we're being called as @chris_plugin or @chris_plugin().
    if main is None:
        # We're called with parens.
        return wrap

    # We're called as @chris_plugin without parens.
    return wrap(main)


_MainArgs = namedtuple('_MainArgs', ['options', 'inputdir', 'outputdir'])


def _call_from_python(args: tuple) -> _MainArgs:
    if len(args) == 2:
        return _MainArgs(options=args[0], inputdir=None, outputdir=args[1])
    if len(args) == 3:
        return _MainArgs(options=args[0], inputdir=args[1], outputdir=args[2])
    raise ValueError(f'decorated main was given: {args}')


def _call_from_cli(parser: argparse.ArgumentParser) -> _MainArgs:
    options = parser.parse_args()
    return _MainArgs(
        options=options,
        inputdir=(options.inputdir if hasattr(options, 'inputdir') else None),
        outputdir=options.outputdir
    )
