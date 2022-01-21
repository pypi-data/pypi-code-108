# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['signingsavvy']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'poetry-core>=1.0.7,<2.0.0',
 'quart>=0.16.2,<0.17.0',
 'requests>=2.26.0,<3.0.0',
 'virtualenv>=20.10.0,<21.0.0']

setup_kwargs = {
    'name': 'signingsavvy',
    'version': '1.0.7',
    'description': 'SigningSavvy API wrapper',
    'long_description': '<h1 align="center">signingsavvy</h1>\n\n<div align="center">\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) [![license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/blackboardd/magui/blob/main/LICENSE) [![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/) [![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org) [![.github/workflows/ci.yml](https://github.com/blackboardd/signingsavvy/actions/workflows/ci.yml/badge.svg)](https://github.com/blackboardd/signingsavvy/actions/workflows/ci.yml)  [![Follow on Twitter](https://img.shields.io/twitter/follow/blkboardd.svg?label=follow+blkboardd)](https://twitter.com/blkboardd)\n\n</div>\n\n## 👠 Features\n\n- API\n- Quart usage\n\n## Changelog\n\nIf you have recently updated, please read the [changelog](/docs/CHANGELOG.md) for details of what has changed.\n\n## 🧑\u200d🤝\u200d🧑 Contributing\n\nRead the [contributing guide](/docs/CONTRIBUTING.md) to learn about our development process, and how to craft proposals.\n\n## ⚖️ License\n\nThis project is licensed under the terms of the [MIT license](/docs/LICENSE).\n',
    'author': 'Brighten Tompkins',
    'author_email': 'brightenqtompkins@gmail.com',
    'maintainer': 'Brighten Tompkins',
    'maintainer_email': 'brightenqtompkins@gmail.com',
    'url': 'https://blackboardd.github.io/signingsavvy/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
