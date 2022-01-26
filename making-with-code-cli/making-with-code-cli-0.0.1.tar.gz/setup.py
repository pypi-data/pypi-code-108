# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['making_with_code_cli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'click>=8.0.3,<9.0.0', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['mwc = making_with_code_cli.cli:cli']}

setup_kwargs = {
    'name': 'making-with-code-cli',
    'version': '0.0.1',
    'description': 'Courseware for Making With Code',
    'long_description': "# MWC CLI\n\n## Development\n\n\nFrom the project root, create a virtual environment and install the\ndependencies. Then follow \n[Click's documentation](https://click.palletsprojects.com/en/8.0.x/#documentation), \nand install the cli as an editable distribution.\n\n```\n$ python -m venv env\n$ source env/bin/activate\n$ pip install -r requirements.txt\n$ pip install --editable mwc_cli\n$ mwc ---help\n```\n\nInitial proposed flow:\n\nIn the flow below:\n\n- MWC is initialized with a name and email address. These will be used with git,\n  and git credentials are used as defaults. Since no host is given, localhost is\n  assumed as the server URL.\n- Create a new course and populate with student info from a CSV file. The\n  `--distribute` flag means also create a distribution of the course.\n- \n\n```\n$ mwc init --username chris --email chris@chrisproctor.net\n$ mwc course new cs9 --roster students.csv --distribute\n$ mwc course list\ncs9:\n - cs9-0\n$ mwc assignment new drawing --repo https://github.com/the-isf-academy/drawing --course cs9-0 --distribute\n$ mwc assignment init drawing-0\n$ mwc assignment status drawing\nName    Repo                                                Commits    Milestones\n------  ------------------------------------------------  ---------  ------------\nJacob   https://github.com/the-isf-academy/drawing-jacob          5             3\nJenny   https://github.com/the-isf-academy/drawing-jenny          6             2\nChris   https://github.com/the-isf-academy/drawing-chris          2             0\n$\n```\n\n## WIP 2021-08-11\n\nThe next thing I need to do is build a way to import course, unit, and\nassignment data. To do this, I need to get the MWC hugo site building its json\ncorrectly. \n\nThen I can work on deploying an assignment\n\nCloning student repos with the right permissions\nPushing updates to student repos\nOrganizing the backlog of repos and the backlog of labs\n\nmwc assignment import http://cs.fablearn.org/courses/cs9/unit00/project/networking.yaml\n\nmwc assignment deploy --name Networking --section CS10.A --dryrun\n\nmwc assignment status --name Networking\n",
    'author': 'Chris Proctor',
    'author_email': 'chris@chrisproctor.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cproctor/making-with-code-courseware',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
