"""
# Python *ChRIS* Plugin Support

Welcome to the documentation for `@chris_plugin`.

## Getting Started

Take a look at the
[README](https://github.com/FNNDSC/chris_plugin#readme)
and [examples](https://github.com/FNNDSC/chris_plugin/tree/master/examples).

A walk-through can be found on our
[wiki](https://github.com/FNNDSC/chris_plugin/wiki/HOW-TO:-Convert-an-existing-Python-app).

## Core API

`chris_plugin` is a decorator which transforms an ordinary
python function into a *ChRIS* plugin.

```python
from chris_plugin import chris_plugin
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--name', required=True)

@chris_plugin(parser=parser, title='Example')
def main(options, inputdir, outpudri):
    print(f'hello, {parser.name}')
```

## Helper Functions

This library also provides helper functions for common use cases,
such as `chris_plugin.vectorize`.

```python
import shutil
from pathlib import Path
from chris_plugin import vectorize

@vectorize(name_mapper='.out')
def copy(input_file: Path, output_file: Path):
    print(f'Copying {input_file} to {output_file}')
    shutil.copyfile(input_file, output_file)
```

"""

from chris_plugin.chris_plugin import chris_plugin
from chris_plugin.mapper import vectorize
import chris_plugin.types as types

__docformat__ = 'numpy'

__all__ = [
    'chris_plugin',
    'vectorize',
    'types'
]