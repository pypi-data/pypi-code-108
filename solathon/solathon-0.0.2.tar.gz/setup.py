# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['solathon', 'solathon.core']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.4.0,<2.0.0',
 'base58>=2.1.1,<3.0.0',
 'construct>=2.10.67,<3.0.0',
 'httpx>=0.21.2,<0.22.0']

setup_kwargs = {
    'name': 'solathon',
    'version': '0.0.2',
    'description': 'High performance, easy to use and feature-rich Solana SDK for Python.',
    'long_description': '<p align="center">\n  <a href="#">\n    <img\n      alt="Solathon logo"\n      src="https://media.discordapp.net/attachments/807140294764003350/929017682836193410/logo.png"\n      width="140"\n    />\n  </a>\n</p>\n\n\n<p align="center">\n  <a href="https://pypi.org/project/solathon/" target="_blank"><img src="https://badge.fury.io/py/solathon.svg" alt="PyPI version"></a>\n  <a href="https://deepsource.io/gh/GitBolt/solathon/?ref=repository-badge}" target="_blank"><img src="https://deepsource.io/gh/GitBolt/solathon.svg/?label=active+issues&show_trend=true&token=O-2BAnF5y1x-YJyaIe-p4hsK" alt="DeepSource" /></a>\n  <a href="https://github.com/GitBolt/solathon/blob/master/LICENSE" target="_blank"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>\n  <br>\n</p>\n\n<h1 align="center">Solathon</h1>\n\nSolathon is an high performance, easy to use and feature-rich Solana SDK for Python. Easy for beginners, powerful for real world applications.\n\n|🧪| The project is in beta phase|\n|---|-----------------------------|\n\n# ✨ Getting started\n## Installation\n```\npip install solathon\n```\n## Client example\n```python\nfrom solathon import Client\n\nclient = Client("https://api.devnet.solana.com")\n```\n## Basic usage example\n```python\n# Basic example on generating a random public key and fetching it\'s balance\nfrom solathon import Client, PublicKey\n\nclient = Client("https://api.devnet.solana.com")\npublic_key = PublicKey(1) # Creating a random public key\n\nbalance = client.get_balance(public_key)\nprint(balance)\n```\n\n# 🗃️ Contribution\nJust drop a pull request lol\n',
    'author': 'GitBolt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/GitBolt/solathon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
