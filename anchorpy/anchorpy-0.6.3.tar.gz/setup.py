# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['anchorpy',
 'anchorpy.coder',
 'anchorpy.program',
 'anchorpy.program.namespace',
 'anchorpy.utils']

package_data = \
{'': ['*']}

install_requires = \
['apischema>=0.16.6,<0.17.0',
 'borsh-construct>=0.1.0,<0.2.0',
 'construct-typing>=0.5.1,<0.6.0',
 'jsonrpcclient>=4.0.1,<5.0.0',
 'more-itertools>=8.11.0,<9.0.0',
 'pyheck>=0.1.4,<0.2.0',
 'pytest-xprocess>=0.18.1,<0.19.0',
 'solana>=0.21.0,<0.22.0',
 'sumtypes>=0.1a6,<0.2',
 'toolz>=0.11.2,<0.12.0',
 'websockets>=10.0,<11.0',
 'zstandard>=0.16.0,<0.17.0']

extras_require = \
{'cli': ['typer>=0.4.0,<0.5.0', 'ipython>=7.30.1,<8.0.0']}

entry_points = \
{'console_scripts': ['anchorpy = anchorpy.cli:app'],
 'pytest11': ['pytest_anchorpy = anchorpy.pytest_plugin']}

setup_kwargs = {
    'name': 'anchorpy',
    'version': '0.6.3',
    'description': 'The Python Anchor client.',
    'long_description': '# AnchorPy\n<div align="center">\n    <img src="https://raw.githubusercontent.com/kevinheavey/anchorpy/main/docs/img/logo.png" width="70%" height="70%">\n</div>\n\n---\n\n[![Discord Chat](https://img.shields.io/discord/889577356681945098?color=blueviolet)](https://discord.gg/sxy4zxBckh)  \n\nAnchorPy is the Python client for [Anchor](https://github.com/project-serum/anchor). It allows you to interact with Anchor programs using Python.\n\nRead the [Documentation](https://kevinheavey.github.io/anchorpy/).\n\n\n\n## Installation\n\n```sh\npip install anchorpy\n\n```\n\n\n### Development Setup\n\nIf you want to contribute to AnchorPy, follow these steps to get set up:\n\n1. Install [poetry](https://python-poetry.org/docs/#installation)\n2. Install dev dependencies:\n```sh\npoetry install\n\n```\n3. Install [nox-poetry](https://github.com/cjolowicz/nox-poetry) (note: do not use Poetry to install this, see [here](https://medium.com/@cjolowicz/nox-is-a-part-of-your-global-developer-environment-like-poetry-pre-commit-pyenv-or-pipx-1cdeba9198bd))\n4. Activate the poetry shell:\n```sh\npoetry shell\n\n```\n',
    'author': 'kevinheavey',
    'author_email': 'kevinheavey123@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kevinheavey/anchorpy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
