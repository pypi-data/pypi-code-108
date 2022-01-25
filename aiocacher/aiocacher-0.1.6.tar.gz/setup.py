# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiocacher',
 'aiocacher.backends',
 'aiocacher.plugins',
 'aiocacher.serializers']

package_data = \
{'': ['*']}

install_requires = \
['aioredis>=2.0.0', 'hiredis>=2.0.0', 'toolz>=0.11.0']

extras_require = \
{'dill': ['dill>=0.3.4'], 'ujson': ['ujson>=5.1.0']}

setup_kwargs = {
    'name': 'aiocacher',
    'version': '0.1.6',
    'description': 'Python asyncio caching decorator backed by a Redis server or cluster.',
    'long_description': None,
    'author': 'Blake VandeMerwe',
    'author_email': 'blakev@null.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
