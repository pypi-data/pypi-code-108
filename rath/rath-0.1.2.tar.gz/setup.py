# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rath']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'koil>=0.1.59,<0.2.0']

setup_kwargs = {
    'name': 'rath',
    'version': '0.1.2',
    'description': 'aiohttp powered apollo like graphql client',
    'long_description': '# rath\n\n[![codecov](https://codecov.io/gh/jhnnsrs/rath/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/rath)\n[![PyPI version](https://badge.fury.io/py/rath.svg)](https://pypi.org/project/rath/)\n[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/rath/)\n![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rath.svg)](https://pypi.python.org/pypi/rath/)\n[![PyPI status](https://img.shields.io/pypi/status/rath.svg)](https://pypi.python.org/pypi/rath/)\n[![PyPI download month](https://img.shields.io/pypi/dm/rath.svg)](https://pypi.python.org/pypi/rath/)\n\n### DEVELOPMENT\n\n## Inspiration\n\nRath is an Apollo (that typescript thing) like library for python, it supports a link like structure\nto facilitate and multiple links\n\n## Features\n\n- includes modular links to support specificatiosn for\n\n  - Subscriptions (via websockets)\n  - File Uploads (multipart specifications)\n\n- Works well with turms created queries\n\n## Installation\n\n```bash\npip install rath\n```\n\n## Usage Query\n\n```python\nfrom rath.links.auth import AuthTokenLink\nfrom rath.links.aiohttp import AioHttpLink\nfrom rath.gql import gql\n\nauth = AuthTokenLink(token_loader=aload_token)\nlink = AioHttpLink(url="http://localhost:3000/graphql")\n\n\nrath = Rath(links=[auth,link])\n\nrath.connect()\n\nquery = qgl("query space ex")\n\nresult = rath.execute(query)\n```\n\nGenerate beautifully typed Operations, Enums,...\n\n### Why Rath\n\nWell "apollo" is already taken as a name, and rath (according to wikipedia) is an etruscan deity identified with Apollo.\n\n## Examples\n\nThis github repository also contains an example client with a turms generated query with the public SpaceX api, as well as a sample of the generated api.\n\n## CLI\n\n```bash\nrath run\n```\n',
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
