# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['begin', 'begin.cli']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['begin = begin.cli.cli:main']}

setup_kwargs = {
    'name': 'begin-cli',
    'version': '0.4.0',
    'description': 'A utility for running targets in a targets.py file',
    'long_description': '# `begin` - v0.4.0\n[![image](https://img.shields.io/pypi/v/begin-cli.svg)](https://pypi.org/project/begin-cli/)\n[![image](https://img.shields.io/pypi/l/begin-cli.svg)](https://pypi.org/project/begin-cli/)\n[![image](https://img.shields.io/pypi/pyversions/begin-cli.svg)](https://pypi.org/project/begin-cli/)\n![tests](https://github.com/LachlanMarnham/begin/actions/workflows/tests.yml/badge.svg?branch=master)\n![flake8](https://github.com/LachlanMarnham/begin/actions/workflows/flake8.yml/badge.svg?branch=master)\n[![codecov](https://codecov.io/gh/LachlanMarnham/begin/branch/master/graph/badge.svg)](https://codecov.io/gh/LachlanMarnham/begin)\n\n\n## Usage\n```bash\nbegin <target_name>@<registry_name> [<key>:<value>]\n```\n1. Arguments to be passed to targets should take the form `<arg_name>:<arg_value>`\n2. Registry names must not contain a colon\n3. Target names must not contain a colon or an `@`\n4. If a target name, registry name or argument value contains whitespace, it must be\nwrapped in single quotes.\n',
    'author': 'Lachlan Marnham',
    'author_email': None,
    'maintainer': 'Lachlan Marnham',
    'maintainer_email': None,
    'url': 'https://github.com/LachlanMarnham/begin',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
