# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tordle']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'isort>=5.10.1,<6.0.0',
 'rich>=11.0.0,<12.0.0',
 'textual>=0.1.14,<0.2.0',
 'toml>=0.10.2,<0.11.0',
 'yapf>=0.32.0,<0.33.0']

entry_points = \
{'console_scripts': ['tordle = tordle.tordle:main']}

setup_kwargs = {
    'name': 'tordle',
    'version': '0.1.2',
    'description': 'A command-line word game.',
    'long_description': '# Tordle!\n\nHave you  fallen for the recent [Wordle](https://www.powerlanguage.co.uk/wordle/) trend? Want to play some more, and don\'t want to leave your terminal? Well `tordle` is for you!\n\nTordle does not connect to wordle. Instead, words are selected on the fly. Additionally, the game can be customized, if you\'re looking to expand the game.\n\n\n![Usage gif](tordle.gif)\n\n\n## Installation:\n\n```\npip install tordle\n```\n\n## Usage\n\n```\ntordle\n```\n\n## Options\n\n- `--target-length`: Specify the size of the taget word.\n- `--total-guesses`: Specify the number of tries to guess the correct word.\n- `--no-alphabet`: Hide the "hint alphabet" that shows which letters you still\n  have available.\n\n## Roadmap:\n\n- Add a hard mode, which requires future guesses to use past hints.\n- Add an evil mode.\n\n\n',
    'author': 'Justin Sybrandt',
    'author_email': 'justin@sybrandt.com',
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
