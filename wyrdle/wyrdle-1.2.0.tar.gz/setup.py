# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wyrdle', 'wyrdle.backend', 'wyrdle.common', 'wyrdle.frontend']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0',
 'sshkeyboard>=2.3.1,<3.0.0',
 'typed-argument-parser>=1.7.2,<2.0.0']

entry_points = \
{'console_scripts': ['wordle = wyrdle.frontend.interface:cli',
                     'wyrdle = wyrdle.frontend.interface:cli']}

setup_kwargs = {
    'name': 'wyrdle',
    'version': '1.2.0',
    'description': 'Wordle and bot in Python',
    'long_description': "# Wyrdle\n![Funny badge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)\n\nThis is a Python implementation of the viral word game, [Wordle](https://www.powerlanguage.co.uk/wordle/), by [Josh Wardle](https://www.powerlanguage.co.uk/) (ohh, so that's where the name is from).\n\nAdditionally, a bot is included that tries to win the game with its own strategy!\n\n## Installation\nInstall from PyPI using\n```sh\npip install wyrdle\n```\n\n## Usage\nYou can play today's Wordle right from your terminal! Simply run\n```sh\nwordle\n```\n\nFeeling lazy? Feeling competitive? (We're going full Google search button here.)  \nThen let the bot play:\n```sh\nwordle -b\n```\n\n### Example\nHere is the bot's run against `smile`:\n> Wordle 666 2/6  \n>   \n> 🟩🟨⬛⬛🟩  \n> 🟩🟩🟩🟩🟩  \n\nImpressive!\n",
    'author': 'Cole French',
    'author_email': '16979554+ColeFrench@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ColeFrench/wyrdle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
