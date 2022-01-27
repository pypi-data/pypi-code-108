# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['transitions_anyio']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3,<4', 'transitions>=0.8.6,<0.9.0']

setup_kwargs = {
    'name': 'transitions-anyio',
    'version': '0.3.0',
    'description': 'An extension for the transitions state machine library which runs asynchronous state machines using anyio.',
    'long_description': "=================\ntransitions-anyio\n=================\n\n.. image:: https://img.shields.io/badge/version-v0.1.0-orange.svg\n        :alt: Version\n        :target: https://github.com/pytransitions/transitions-anyio\n\n.. image:: https://img.shields.io/pypi/v/transitions-anyio.svg\n        :alt: PyPI\n        :target: https://pypi.org/project/transitions-anyio\n\n.. image:: https://img.shields.io/github/commits-since/pytransitions/transitions-anyio/0.1.0.svg\n        :alt: GitHub Commits\n        :target: https://github.com/pytransitions/transitions-anyio/compare/0.1.0...master\n\n.. image:: https://img.shields.io/github/license/pytransitions/transitions-anyio.svg\n         :alt: License\n         :target: https://github.com/pytransitions/transitions-anyio/blob/master/LICENSE\n\nAn extension for the `transitions`_ state machine library\nwhich runs asynchronous state machines using `anyio`_.\n\nThis library provides the `AnyIOMachine`, `AnyIOGraphMachine`, `HierarchicalAnyIOMachine`\nand the `HierarchicalAnyIOGraphMachine` variants.\nThey function exactly like their respective `Async*` variants.\nPlease refer to transitions' documentation for usage examples.\n\n.. _transitions: https://github.com/pytransitions/transitions\n.. _anyio: https://github.com/agronholm/anyio",
    'author': 'Alexander Neumann',
    'author_email': 'aleneum@gmail.com',
    'maintainer': 'Omer Katz',
    'maintainer_email': 'omer.drow@gmail.com',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
