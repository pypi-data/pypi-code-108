# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskloop']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'prompt-toolkit>=3.0.24,<4.0.0',
 'rich>=11.0.0,<12.0.0',
 'taskw>=1.3.1,<2.0.0']

entry_points = \
{'console_scripts': ['taskloop = taskloop.loop:main']}

setup_kwargs = {
    'name': 'taskloop',
    'version': '0.2.0',
    'description': 'Taskwarrior utility to continually loop through and add tasks to a project',
    'long_description': "# Taskloop\n\nThis utility allows you to create multiple tasks for a\n[Taskwarrior](https://taskwarrior.org) project.\n\n# Installation\n## via PyPi\n` pip install taskloop`\n## via git (development)\n1. Clone this repo\n2. cd taskloop\n3. `poetry run taskloop/loop.py`\n# Running\n> Note: Currently this is in early development and doesn't actually do anything\n> except demo an autocomplete of your projects\nAfter pip installing, you may run\n\n`taskloop`\n\nThis requires you have a taskrc at ~/.config/task/taskrc.\n\nMore flexibility is planned for this though.  If you have an old style\n~/.taskrc, you should be able to symlink it with `mkdir -p ~/.config/task/taskrc\n&& ln -s ~/.taskrc ~/.config/task/taskrc`\n",
    'author': 'Alex Kelly',
    'author_email': 'kellya@arachnitech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kellya/taskloop',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
