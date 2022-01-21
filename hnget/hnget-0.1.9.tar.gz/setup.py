# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hnget']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.6.3,<5.0.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['hnget = hnget.application:main']}

setup_kwargs = {
    'name': 'hnget',
    'version': '0.1.9',
    'description': 'Shows and opens links on Hacker news from the terminal',
    'long_description': '#  hnget - Hacker News web scraper\n\nA commandline program for browsing [Hacker News](https://news.ycombinator.com).\n\n![Hnget Screenshot](extras/screen.png)\n\n## Usage\n\n`hnget --fetch (--f)`\n\nPrint the top 30 posts on Hacker News, enumerated. `--fetch` takes an optional integer value to specify different pages of the results.\n\n`hnget --open (--o) [NUMS...]`\n\nOpen stories in default web browser. Multiple values are\naccepted. Default web browser can be set with `$BROWSER`.\n\n`hnget --comments (--o) [NUMS...]`\n\nLike `--open`, but view the comment page(s) instead.\n\n`hnget --fetch --best`\n\nView the top posts for the week instead of the current front page.\n\n## Installation\n\nWith Pypi:\n\n`$ pip install hnget`\n\nManually:\n\n$ `git clone https://github.com/jsbmg/hnget`\n\n$ `cd hnget`\n\n$ `pip install . pyproject.toml`\n',
    'author': 'Jordan Sweet',
    'author_email': 'hello@jordandsweet.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
