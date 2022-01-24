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
    'version': '0.4.0',
    'description': 'Taskwarrior utility to continually loop through and add tasks to a project',
    'long_description': '# Taskloop\n\nThis utility allows you to create multiple tasks for a\n[Taskwarrior](https://taskwarrior.org) project.\n\n# Installation\n\n## via PyPi\n` pip install taskloop`\n\n## via git (development)\n1. Clone this repo\n2. cd taskloop\n3. Add deps using poetry `poetry install`\n4. `poetry run taskloop/loop.py`\n\n# Running\nAfter pip installing, you may run\n\n`taskloop`\n\nThis requires you have a taskrc at ~/.config/task/taskrc.\n\nMore flexibility is planned for this though.  If you have an old style\n~/.taskrc, you should be able to symlink it with `mkdir -p ~/.config/task/taskrc\n&& ln -s ~/.taskrc ~/.config/task/taskrc`\n\n## Entering tasks\nYou will be prompted for a project.  This will autocomplete from your list of\nprojects (currently only pending, planned to optionally pull from "completed"\nalso)\n\nAfter entering a project, you will loop through adding tasks to the project.  if\nyou want to make your task dependent on the last task, start your task with a\nperiod.\n\nEntry will continue to loop until you end by entering an empty line\n\nNow sync will be attempted.   There are currently no checks in place, so if you\ndon\'t have a taskserver configured,this will fail.\n\n# Screencast Demo\n[![asciicast](https://asciinema.org/a/B5IzyeUWdGRjK1bUtCjy52gpp.svg)](https://asciinema.org/a/B5IzyeUWdGRjK1bUtCjy52gpp)\n',
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
