# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dirty_equals']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dirty-equals',
    'version': '0',
    'description': 'Using __eq__ for dirty, but extremely useful things.',
    'long_description': '# dirty-equals\n\n[![CI](https://github.com/samuelcolvin/dirty-equals/workflows/CI/badge.svg?event=push)](https://github.com/samuelcolvin/dirty-equals/actions?query=event%3Apush+branch%3Amaster+workflow%3ACI)\n[![Coverage](https://codecov.io/gh/samuelcolvin/dirty-equals/branch/master/graph/badge.svg)](https://codecov.io/gh/samuelcolvin/dirty-equals)\n[![pypi](https://img.shields.io/pypi/v/dirty-equals.svg)](https://pypi.python.org/pypi/dirty-equals)\n[![versions](https://img.shields.io/pypi/pyversions/dirty-equals.svg)](https://github.com/samuelcolvin/dirty-equals)\n[![license](https://img.shields.io/github/license/samuelcolvin/dirty-equals.svg)](https://github.com/samuelcolvin/dirty-equals/blob/master/LICENSE)\n\nUsing `__eq__` for dirty, but extremely useful things.\n\n## Install\n\n```bash\npip install dirty-equals\n```\n\n## Usage\n\nTODO.\n',
    'author': 'Samuel Colvin',
    'author_email': 's@muelcolvin.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/samuelcolvin/dirty-equals',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
