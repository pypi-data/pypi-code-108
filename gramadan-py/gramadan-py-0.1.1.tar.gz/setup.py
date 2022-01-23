# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gramadan', 'gramadan.tester', 'gramadan.v2', 'v2']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.7.1,<5.0.0', 'tabulate>=0.8.9,<0.9.0']

setup_kwargs = {
    'name': 'gramadan-py',
    'version': '0.1.1',
    'description': "Pure Python implementation of michmech's C# Gramadán utility for manipulating the Irish National Morphology Database",
    'long_description': "# GramadánPy\n\n_With thanks to [michmech (Michal Měchura)](https://github.com/michmech/)!_\n\n*[UNOFFICIAL]* A pure Python conversion of michmech's [Gramadán](https://github.com/michmech/Gramadan).\n\nNote that, at present, the Python is _not_ idiomatic. It is intentionally kept similar to\nthe original C#, although primarily in paradigm. The code here is extensively typed,\nand passes both mypy and black checkers.\n\n## Installation\n\nThis can be installed with [poetry](https://python-poetry.org/):\n\n    poetry install\n\nThe test suite can be executed, from this directory.\n\n## Tests\n\nIf you do not wish to install or run the .NET setup, you can still execute the pure Python\ntest suite:\n\n    poetry run pytest tests/python\n\n## Comparison Checking\n\nThis directory contains a tool that can be run:\n\n    ./comparison.sh\n\nThis has been set up (at present) to run from the working directory.\n\nIt assumes that you have built the C# Tester.csproj project in the /Tester folder and\nthat a binary exists at `../Tester/bin/Debug/Tester.exe`\n\nPath separators are currently Linux, to simplify visual code comparison, but these can\nbe made OS-independent.\n\nFor the purposes of comparison, the following `xbuild` was used:\n\n    XBuild Engine Version 14.0\n    Mono, Version 6.8.0.105\n    Copyright (C) 2005-2013 Various Mono authors\n\nThe command executed in the Tester folder was:\n\n    xbuild\n\nThe equivalent Python was originally compared with Python 3.9.7\n",
    'author': "Phil Weir (Python conversion Michal Měchura's work)",
    'author_email': 'phil.t.weir@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
