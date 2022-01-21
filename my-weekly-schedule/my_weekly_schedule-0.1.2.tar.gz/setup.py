# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['my_weekly_schedule']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0', 'pydantic>=1.9.0,<2.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['my_weekly_schedule = my_weekly_schedule.main:app']}

setup_kwargs = {
    'name': 'my-weekly-schedule',
    'version': '0.1.2',
    'description': 'A tool for plotting your weekly schedule.',
    'long_description': '# my_weekly_schedule\n\nPlot your weekly schedule from a simple text file with Python.\n\nInspired by [utkuufuk/weekplot](https://github.com/utkuufuk/weekplot).\n\n![Schedule](example.png)\n\n## Installation\n\nRun `pip install my_weekly_schedule` for the latest stable version.\n\n### Development\n\nThis project uses [Python Poetry](https://python-poetry.org/) for dependency management.\nYou can install Python Poetry with the [following instructions](https://python-poetry.org/docs/#installation).\n\n``` sh\npoetry install\n```\n\nTo run the code during development:\n\n``` sh\npoetry run python my_weekly_schedule/main.py example.txt\n```\n\n## Usage\n\nYou can run the default options with:\n\n```sh\nmy_weekly_schedule example.txt\n```\n\nYou can replace `example.txt` with your own schedule files.\n\nYou can list all CLI options with:\n\n```sh\nmy_weekly_schedule --help\n```\n\n#### Example input files\n - [text](example.txt)\n\n## Colors\n\nYou can use any color in [the CSS3 specification](https://www.w3.org/TR/css-color-3/#svg-color).\n',
    'author': 'Fabian Torres',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ftorres16/my_weekly_schedule',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
