# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pingdomcli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['pdcli = pingdomcli.pdcli:main']}

setup_kwargs = {
    'name': 'pingdomcli',
    'version': '0.3.0',
    'description': 'CLI to interact with Pingdom API',
    'long_description': None,
    'author': 'Alex Kelly',
    'author_email': 'alex.kelly@franklin.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
