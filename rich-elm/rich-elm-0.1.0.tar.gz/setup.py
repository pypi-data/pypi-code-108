# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rich_elm']

package_data = \
{'': ['*']}

install_requires = \
['fuzzywuzzy>=0.18.0,<0.19.0',
 'lorem-text>=2.1,<3.0',
 'prompt-toolkit>=3.0.24,<4.0.0',
 'python-Levenshtein>=0.12.2,<0.13.0',
 'returns>=0.18.0,<0.19.0',
 'rich>=11.0.0,<12.0.0',
 'textual>=0.1.14,<0.2.0']

setup_kwargs = {
    'name': 'rich-elm',
    'version': '0.1.0',
    'description': 'Elm-style architecture for TUI apps, powered by Rich',
    'long_description': '',
    'author': 'Aatif Syed',
    'author_email': 'aatifsyedyp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aatifsyed/rich-elm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
