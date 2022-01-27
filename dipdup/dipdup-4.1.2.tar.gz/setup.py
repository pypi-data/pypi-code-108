# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dipdup',
 'dipdup.datasources',
 'dipdup.datasources.bcd',
 'dipdup.datasources.coinbase',
 'dipdup.datasources.metadata',
 'dipdup.datasources.tzkt',
 'dipdup.test',
 'dipdup.utils']

package_data = \
{'': ['*'],
 'dipdup': ['configs/*',
            'sql/on_reindex/*',
            'templates/*',
            'templates/docker/*']}

install_requires = \
['APScheduler>=3.7.0,<4.0.0',
 'aiohttp>=3.8.0,<4.0.0',
 'aiolimiter>=1.0.0-beta.1,<2.0.0',
 'anyio>=3.2.1,<4.0.0',
 'asyncclick>=8.0.1,<9.0.0',
 'asyncpg>=0.24.0,<0.25.0',
 'datamodel-code-generator>=0.11.1,<0.12.0',
 'fcache>=0.4.7,<0.5.0',
 'pydantic>=1.8.1,<2.0.0',
 'pyhumps>=3.0.2,<4.0.0',
 'pysignalr>=0.1.1,<0.2.0',
 'python-dotenv>=0.18.0,<0.19.0',
 'ruamel.yaml>=0.17.2,<0.18.0',
 'sentry-sdk>=1.1.0,<2.0.0',
 'sqlparse>=0.4.1,<0.5.0',
 'tabulate>=0.8.9,<0.9.0',
 'tortoise-orm==0.17.8',
 'typing-inspect>=0.6.0,<0.7.0']

extras_require = \
{'pytezos': ['pytezos>=3.2.4,<4.0.0']}

entry_points = \
{'console_scripts': ['dipdup = dipdup.cli:cli']}

setup_kwargs = {
    'name': 'dipdup',
    'version': '4.1.2',
    'description': 'Python SDK for developing indexers of Tezos smart contracts inspired by The Graph',
    'long_description': "# DipDup\n\n[![PyPI version](https://badge.fury.io/py/dipdup.svg?)](https://badge.fury.io/py/dipdup)\n[![Tests](https://github.com/dipdup-net/dipdup-py/workflows/Tests/badge.svg?)](https://github.com/baking-bad/dipdup/actions?query=workflow%3ATests)\n[![Made With](https://img.shields.io/badge/made%20with-python-blue.svg?)](ttps://www.python.org)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\nPython SDK for developing indexers of [Tezos](https://tezos.com/) smart contracts inspired by [The Graph](https://thegraph.com/).\n\n## Quickstart\n\nPython 3.8+ is required for dipdup to run.\n\n```shell\n$ pip install dipdup\n```\n\n* Read the rest of the tutorial: [docs.dipdup.net](https://docs.dipdup.net/)  \n* Check out [demo projects](https://github.com/dipdup-net/dipdup-py/tree/master/src)\n\n## Contribution\n\nTo set up development environment you need to install [poetry](https://python-poetry.org/docs/#installation) package manager and GNU Make. Then run one of the following commands at project's root:\n\n```shell\n$ # install project dependencies\n$ make install\n$ # run linters\n$ make lint\n$ # run tests\n$ make test cover\n$ # run full CI pipeline\n$ make\n```\n\n## Contact\n* Telegram chat: [@baking_bad_chat](https://t.me/baking_bad_chat)\n* Slack channel: [#baking-bad](https://tezos-dev.slack.com/archives/CV5NX7F2L)\n* Discord group: [Baking Bad](https://discord.gg/JZKhv7uW)\n\n## About\nThis project is maintained by [Baking Bad](https://baking-bad.org/) team.  \nDevelopment is supported by [Tezos Foundation](https://tezos.foundation/).\n",
    'author': 'Lev Gorodetskiy',
    'author_email': 'github@droserasprout.space',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dipdup.net/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
