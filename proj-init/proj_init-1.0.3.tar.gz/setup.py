# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proj_init']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0']

entry_points = \
{'console_scripts': ['proj_init = proj_init.create:proj_init']}

setup_kwargs = {
    'name': 'proj-init',
    'version': '1.0.3',
    'description': 'Initialize you github projects with a one liner',
    'long_description': "# Project Initializer\n\nEverytime you want to start a project you do the basics. go to your projects folder, create a new folder for the project, do your git commands, sync the repo, add a README file and push your initial commit.\n\nThat is what this simple project is for, making your life easier, and doing all that automatically for you.\n\n## Setting up:\n\n1. Install the project.\n```bash\n$ pip install proj-init\n```\n\n2. Create environment variables:\n\n    - `GIT_AUTOMATION = Github Personal Access Token`\n    - `PROJECTS = Default path where to create the projects` (Optional, if you don't set this variable the default path will be the current directory)\n\n3. Usage:\n```\nproj_init [-h] [-l] [-p] [-d PATH] <repo_name>\n\nAutomate your workflow with proj_init command.\n\npositional arguments:\n  <repo_name>           Name of your repo to be created.\n\noptions:\n  -h, --help            show this help message and exit\n  -l, --local           Creates your repo only locally.\n  -p, --private         Creates your repo in private mode.\n  -d PATH, --directory PATH\n                        Path where the repo is going to be created.\n```\n\nHappy Coding!\n",
    'author': 'Thales Nunes',
    'author_email': 'thalesaknunes22@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thalesnunes/gcal_notifier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
