# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pomace', 'pomace.tests']

package_data = \
{'': ['*'], 'pomace.tests': ['cassettes/*']}

install_requires = \
['beautifulsoup4>=4.8.2,<5.0.0',
 'bullet>=2.1,<3.0',
 'cached-property>=1.5.2,<2.0.0',
 'cleo>=0.8.1,<0.9.0',
 'datafiles>=1.1,<2.0',
 'fake-useragent>=0.1.11,<0.2.0',
 'faker>=4.1.1',
 'flask-api>=3.0,<4.0',
 'gitman>=3.0,<4.0',
 'inflection>=0.5.1,<0.6.0',
 'ipdb>=0.13.7,<0.14.0',
 'minilog>=2.0,<3.0',
 'parse>=1.14,<2.0',
 'selenium>=4.1,<5.0',
 'splinter>=0.17,<0.18',
 'us>=2.0.2,<3.0.0',
 'webdriver_manager>=2.5,<3.0',
 'zipcodes>=1.1.2,<2.0.0']

entry_points = \
{'console_scripts': ['pomace = pomace.cli:application.run']}

setup_kwargs = {
    'name': 'pomace',
    'version': '0.9.4',
    'description': 'Dynamic page objects for browser automation.',
    'long_description': "# Pomace\n\nDynamic page objects for browser automation.\n\n[![Unix Build Status](https://img.shields.io/github/workflow/status/jacebrowning/pomace/main?label=unix)](https://github.com/jacebrowning/pomace/actions?query=branch%3Amain)\n[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/pomace/main.svg?label=window)](https://ci.appveyor.com/project/jacebrowning/pomace)\n[![Coverage Status](https://img.shields.io/codecov/c/gh/jacebrowning/pomace)](https://codecov.io/gh/jacebrowning/pomace)\n[![PyPI Version](https://img.shields.io/pypi/v/pomace.svg)](https://pypi.org/project/pomace)\n[![PyPI License](https://img.shields.io/pypi/l/pomace.svg)](https://pypi.org/project/pomace)\n\n## Quick Start\n\nOpen **Terminal.app** in macOS and paste:\n\n```shell\npython3 -m pip install --upgrade pomace && python3 -m pomace run\n```\n\nor if you have Homebrew:\n\n```shell\nbrew install pipx; pipx run --no-cache pomace run\n```\n\n## Full Demo\n\nIf you're planning to run Pomace multiple times, install it with [pipx](https://pipxproject.github.io/pipx/) first:\n\n```shell\npipx install pomace\n```\n\nor get the latest version:\n\n```shell\npipx upgrade pomace\n```\n\nThen download some site models:\n\n```shell\npomace clone https://github.com/jacebrowning/pomace-twitter.com\n```\n\nAnd launch the application:\n\n```shell\npomace run twitter.com\n```\n\n# Usage\n\nInstall this library directly into an activated virtual environment:\n\n```shell\npip install pomace\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```shell\npoetry add pomace\n```\n",
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/pomace',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
