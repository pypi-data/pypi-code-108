import argparse
import sys
from pathlib import Path
import functools
from typing import Callable, Optional
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


    Example
    -------

    ```python
    from chris_plugin import chris_plugin
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--name', required=True)

    @chris_plugin(parser=parser, title='Example', min_memory_limit='300Mi')
    def main(options, inputdir, outpudri):
        print(f'hello, {parser.name}')
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
        def wrapper():
            options = parser.parse_args()
            outputdir = Path(options.outputdir)
            _mkdir(outputdir)

            if verified_type == 'fs':
                main(options, outputdir)
            else:
                inputdir = Path(options.inputdir)
                _check_is_dir(inputdir)
                main(options, inputdir, Path(options.outputdir))

        return wrapper

    # See if we're being called as @chris_plugin or @chris_plugin().
    if main is None:
        # We're called with parens.
        return wrap

    # We're called as @chris_plugin without parens.
    return wrap(main)
