# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wordlebee']

package_data = \
{'': ['*'], 'wordlebee': ['data/*']}

install_requires = \
['numpy>=1.22.1,<2.0.0', 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['wordlebee = wordlebee.__main__:cli']}

setup_kwargs = {
    'name': 'wordlebee',
    'version': '0.5.0',
    'description': 'wordle word guessing helper bee',
    'long_description': '<div align="center">\n\n# wordle*bee* 🐝\n\n[![PyPi Version](https://img.shields.io/pypi/v/wordlebee.svg?style=flat-square)](https://pypi.org/project/wordlebee/)\n[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](#license)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](#black)\n</div>\n\nA cli wordle word guessing helper bee to solve the wordle puzzle of the day.\n\n[![asciicast](https://asciinema.org/a/NSZZUpGhajLcDh9xuMGYIDjTs.svg)](https://asciinema.org/a/NSZZUpGhajLcDh9xuMGYIDjTs?t=8)\n\n## Usage\n\n    python -m wordlebee\n\n## Installation\n\nInstall `wordlebee`:\n\n    pip install wordlebee\n\n## Development\n\nInstall conda enviroment:\n\n    conda env create -f environment.yml\n\nInstall using `poetry`:\n\n    poetry install\n',
    'author': 'Mrlento234',
    'author_email': 'lento.manickathan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
