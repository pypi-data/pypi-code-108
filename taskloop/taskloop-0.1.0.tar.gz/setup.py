# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskloop']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'prompt-toolkit>=3.0.24,<4.0.0', 'taskw>=1.3.1,<2.0.0']

entry_points = \
{'console_scripts': ['taskloop = taskloop.loop:main']}

setup_kwargs = {
    'name': 'taskloop',
    'version': '0.1.0',
    'description': 'Taskwarrior utility to continually loop through and add tasks to a project',
    'long_description': None,
    'author': 'Alex Kelly',
    'author_email': 'kellya@arachnitech.com',
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
