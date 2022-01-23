# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vyxal']

package_data = \
{'': ['*']}

install_requires = \
['num2words>=0.5.10,<0.6.0', 'sympy>=1.9,<2.0']

entry_points = \
{'console_scripts': ['vyxal = vyxal.main:cli']}

setup_kwargs = {
    'name': 'vyxal',
    'version': '2.8.0',
    'description': 'A golfing language that has aspects of traditional programming languages.',
    'long_description': "# Vyxal\n\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Vyxal/Vyxal.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Vyxal/Vyxal/context:python) ![Test status](https://github.com/Vyxal/Vyxal/actions/workflows/run-tests.yaml/badge.svg)\n\nVyxal is a golfing language with a unique design philosophy: make things as short as possible but retain elegance while doing so. In very simple terms, this means\nkeeping aspects of traditional programming languages that most developers are familiar with, while still providing commands that allow golfers to actually _win_\nchallenges.\n\nVyxal is _not_ a language which forces users to mash random characters togther until something works. Nor is it a language that needs to be verbose. Vyxal is terse when\nit needs to be, and readable/stylish when it wants to be.\n\nVyxal is also deliberately designed to be an easy language to learn. While it may be possible to teach golfers how to program in Vyxal, it is far more likely that they will just learn through experience. The language is designed to be easy to understand, and to allow for fast development.\n\nUltimately, Vyxal is a language for golfers, by golfers.\n\n## Installation\n\nYou can also use the [online interpreter](https://vyxal.pythonanywhere.com) with no need to install!\n\nIf you only want to run Vyxal, all you need to run is this:\n```\npip install vyxal\n```\n\nIf you are working on Vyxal, install [Poetry](https://python-poetry.org), and then you can clone this repo and run:\n```\npoetry install\n```\n\n## Usage\n\nTo run using the script:\n```\nvyxal <file> <flags (single string of flags)> <input(s)>\n```\n\nIf you're using Poetry:\n```\npoetry run vyxal <file> <flags (single string of flags)> <input(s)>\n```\n\n## Why Make Another Golfing Language When There's Like Hundreds of Them Already?\n\nMost golfing languages are created with the intent of terse code - a goal that is obviously essential to the very core of what a golfing language is. However, this is\nmostly done at the expense of losing constructs within traditional programming languages that make things simple to do. Vyxal's raison d'être is to provide structures\nof practical languages - such as functions, variables and comments - that are oftentimes lost within the modern golfing language market.\n\nAnother reason for Vyxal is to provide an easy to use golfing language that anyone can quickly pick up - by providing tools that both new and experienced users are\nfamiliar with, Vyxal aims to cater to a wide demographic of golfers.\n\nPut simply, Vyxal exists because golfers need a golfing language - and because golfing languages could be better.\n\n## Links\n\n- [Repository](https://github.com/Vyxal/Vyxal)\n- [Online Interpreter](http://vyxal.pythonanywhere.com)\n<!-- TODO: fix broken links\n- [Tutorial](https://github.com/Vyxal/Vyxal/blob/master/docs/Tutorial.md)\n- [Codepage](https://github.com/Vyxal/Vyxal/blob/master/docs/codepage.txt)\n-->\n- [Chat Room (SE Chat)](https://chat.stackexchange.com/rooms/106764/vyxal)\n- [Elements](https://github.com/Vyxal/Vyxal/blob/v2.6.0/documents/knowledge/elements.md)\n- [Vyxapedia](https://vyxapedia.hyper-neutrino.xyz/)\n",
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://vyxal.pythonanywhere.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
