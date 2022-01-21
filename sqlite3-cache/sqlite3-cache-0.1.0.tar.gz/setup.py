# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlite3_cache']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sqlite3-cache',
    'version': '0.1.0',
    'description': 'Use SQLite3 as cache.',
    'long_description': '# SQLite3 Cache\n\n[![Coverage Status][coverage-badge]][coverage]\n[![GitHub Workflow Status][status-badge]][status]\n[![PyPI][pypi-badge]][pypi]\n[![GitHub][licence-badge]][licence]\n[![GitHub Last Commit][repo-badge]][repo]\n[![GitHub Issues][issues-badge]][issues]\n[![Python Version][version-badge]][pypi]\n\n```shell\npip install sqlite3-cache\n```\n\n---\n\n**Documentation**: [https://mrthearman.github.io/sqlite3-cache/](https://mrthearman.github.io/sqlite3-cache/)\n\n**Source Code**: [https://github.com/MrThearMan/sqlite3-cache/](https://github.com/MrThearMan/sqlite3-cache/)\n\n---\n\nUse [SQLite3][sqlite] as quick, persistent, thread-safe cache.\nCan store any [picklable][picklable] objects.\n\n```python\nfrom sqlite3_cache import Cache\n\ncache = Cache()\n```\n\n\n[sqlite]: https://docs.python.org/3/library/sqlite3.html\n[picklable]: https://docs.python.org/3/library/pickle.html\n\n[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/sqlite3-cache/badge.svg?branch=main\n[status-badge]: https://img.shields.io/github/workflow/status/MrThearMan/sqlite3-cache/Tests\n[pypi-badge]: https://img.shields.io/pypi/v/sqlite3-cache\n[licence-badge]: https://img.shields.io/github/license/MrThearMan/sqlite3-cache\n[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/sqlite3-cache\n[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/sqlite3-cache\n[version-badge]: https://img.shields.io/pypi/pyversions/sqlite3-cache\n\n[coverage]: https://coveralls.io/github/MrThearMan/sqlite3-cache?branch=main\n[status]: https://github.com/MrThearMan/sqlite3-cache/actions/workflows/main.yml\n[pypi]: https://pypi.org/project/sqlite3-cache\n[licence]: https://github.com/MrThearMan/sqlite3-cache/blob/main/LICENSE\n[repo]: https://github.com/MrThearMan/sqlite3-cache/commits/main\n[issues]: https://github.com/MrThearMan/sqlite3-cache/issues\n',
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrThearMan/sqlite3-cache',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
