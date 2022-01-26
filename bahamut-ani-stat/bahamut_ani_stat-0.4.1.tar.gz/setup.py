# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bahamut_ani_stat',
 'bahamut_ani_stat.cli',
 'bahamut_ani_stat.db',
 'bahamut_ani_stat.parser',
 'bahamut_ani_stat.plot']

package_data = \
{'': ['*'], 'bahamut_ani_stat.plot': ['static/*']}

install_requires = \
['SQLAlchemy[mypy]>=1.4.20,<2.0.0',
 'bokeh>=2.3.3,<3.0.0',
 'bs4>=0.0.1,<0.0.2',
 'click>=8.0.1,<9.0.0',
 'dataclasses-json>=0.5.4,<0.6.0',
 'httpx>=0.18.2,<0.19.0',
 'lxml>=4.6.3,<5.0.0',
 'pandas>=1.3.0,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'tqdm>=4.61.1,<5.0.0']

setup_kwargs = {
    'name': 'bahamut-ani-stat',
    'version': '0.4.1',
    'description': 'Toolkit for Bahamut ani gamer data',
    'long_description': '[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Github Actions](https://github.com/Lee-W/bahamut_ani_stat/actions/workflows/python-check.yaml/badge.svg)](https://github.com/Lee-W/bahamut_ani_stat/wayback-machine-saver/actions/workflows/python-check.yaml)\n\n[![PyPI Package latest release](https://img.shields.io/pypi/v/bahamut_ani_stat.svg?style=flat-square)](https://pypi.org/project/bahamut_ani_stat/)\n[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/bahamut_ani_stat?style=flat-square)](https://pypi.org/project/bahamut_ani_stat/)\n[![Supported versions](https://img.shields.io/pypi/pyversions/bahamut_ani_stat.svg?style=flat-square)](https://pypi.org/project/bahamut_ani_stat/)\n\n\n# bahamut_ani_stat\n\nToolkit for Bahamut ani gamer data\n\n## Getting Started\n\n### Prerequisites\n* [Python](https://www.python.org/downloads/)\n\n## Usage\n\n\n## Contributing\nSee [Contributing](contributing.md)\n\n## Authors\nWei Lee <weilee.rx@gmail.com>\n\n\nCreated from [Lee-W/cookiecutter-python-template](https://github.com/Lee-W/cookiecutter-python-template/tree/0.9.1) version 0.9.1\n',
    'author': 'Wei Lee',
    'author_email': 'weilee.rx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Lee-W/bahamut_ani_stat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
