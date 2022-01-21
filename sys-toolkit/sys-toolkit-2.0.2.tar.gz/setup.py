# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sys_toolkit',
 'sys_toolkit.configuration',
 'sys_toolkit.system',
 'sys_toolkit.tests']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'inflection>=0.5,<0.6']

entry_points = \
{'pytest11': ['sys_toolkit_fixtures = sys_toolkit.fixtures']}

setup_kwargs = {
    'name': 'sys-toolkit',
    'version': '2.0.2',
    'description': 'Classes for operating system utilities',
    'long_description': None,
    'author': 'Ilkka Tuohela',
    'author_email': 'hile@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
