# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fudgeware']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['fudge = fudgeware.cli:main']}

setup_kwargs = {
    'name': 'fudgeware',
    'version': '0.0.1',
    'description': 'Create and manage diceware passwords with hash-based dice rolls',
    'long_description': '#########\nFudgeware\n#########\n\nCreate and manage diceware passwords with hash-based dice rolls.\n',
    'author': 'Ronni Elken Lindsgaard',
    'author_email': 'ronni.lindsgaard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rlindsgaard/fudgeware',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
