# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['deezer_oauth']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'typer[all]>=0.4.0,<0.5.0']

extras_require = \
{'docs': ['Sphinx>=4.0.0,<5.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0',
          'myst-parser>=0.16.0,<0.17.0']}

entry_points = \
{'console_scripts': ['deezer-oauth = deezer_oauth.main:app']}

setup_kwargs = {
    'name': 'deezer-oauth-cli',
    'version': '0.1.1',
    'description': 'A small CLI to quickly obtain an API token for Deezer API.',
    'long_description': '# Deezer OAuth CLI\n\n<p align="center">\n  <a href="https://github.com/browniebroke/deezer-oauth-cli/actions?query=workflow%3ACI">\n    <img src="https://img.shields.io/github/workflow/status/browniebroke/deezer-oauth-cli/CI/main?label=CI&logo=github&style=flat-square" alt="CI Status" >\n  </a>\n  <a href="https://codecov.io/gh/browniebroke/deezer-oauth-cli">\n    <img src="https://img.shields.io/codecov/c/github/browniebroke/deezer-oauth-cli.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">\n  </a>\n</p>\n<p align="center">\n  <a href="https://python-poetry.org/">\n    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">\n  </a>\n  <a href="https://github.com/ambv/black">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">\n  </a>\n  <a href="https://github.com/pre-commit/pre-commit">\n    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">\n  </a>\n</p>\n<p align="center">\n  <a href="https://pypi.org/project/deezer-oauth-cli/">\n    <img src="https://img.shields.io/pypi/v/deezer-oauth-cli.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">\n  </a>\n  <img src="https://img.shields.io/pypi/pyversions/deezer-oauth-cli.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">\n  <img src="https://img.shields.io/pypi/l/deezer-oauth-cli.svg?style=flat-square" alt="License">\n</p>\n\nA small CLI to quickly obtain an API token for Deezer API.\n\nObtaining API token to develop API applications can be complicated and sometimes feel like a chicken and egg situation: it\'s hard to play with the API without a token, but it can be difficult to get a token without an application to do the OAuth flow.\n\nGiven the app ID and secret, this tool lets you quickly get an API token.\n\n## Installation\n\nInstall this via pip (or your favourite package manager):\n\n`pip install deezer-oauth-cli`\n\n## Usage\n\nBefore starting to use this tool, you first need to declare your Deezer app in [their developer portal](https://developers.deezer.com). Create a new app with the following Redirect URL: `http://localhost:8080/oauth/return`.\n\nOnce created, Deezer will generate an application ID and secret key for you, that\'s the 2 parameters that you need to run this tool:\n\n```shell\n$ deezer-oauth APP_ID APP_SECRET\n```\n\nThis will:\n\n- Spin up a webserver in the background running at `http://localhost:8080`.\n- Open your browser to grant authorisation access to your Deezer account.\n- Redirect to a page showing the API token & expiry.\n- Write the token to a `.env` file.\n\n## Contributors ✨\n\nThanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):\n\n<!-- prettier-ignore-start -->\n<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable -->\n<table>\n  <tr>\n    <td align="center"><a href="https://browniebroke.com/"><img src="https://avatars.githubusercontent.com/u/861044?v=4?s=80" width="80px;" alt=""/><br /><sub><b>Bruno Alla</b></sub></a><br /><a href="https://github.com/browniebroke/deezer-oauth-cli/commits?author=browniebroke" title="Code">💻</a> <a href="#ideas-browniebroke" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/browniebroke/deezer-oauth-cli/commits?author=browniebroke" title="Documentation">📖</a></td>\n  </tr>\n</table>\n\n<!-- markdownlint-restore -->\n<!-- prettier-ignore-end -->\n\n<!-- ALL-CONTRIBUTORS-LIST:END -->\n<!-- prettier-ignore-end -->\n\nThis project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!\n\n## Credits\n\nThis package was created with\n[Cookiecutter](https://github.com/audreyr/cookiecutter) and the\n[browniebroke/cookiecutter-pypackage](https://github.com/browniebroke/cookiecutter-pypackage)\nproject template.\n',
    'author': 'Bruno Alla',
    'author_email': 'alla.brunoo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/browniebroke/deezer-oauth-cli',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
