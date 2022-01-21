# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['httpx_cache', 'httpx_cache.cache', 'httpx_cache.serializer']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.4.0,<4.0.0',
 'attrs>=21.4.0,<22.0.0',
 'fasteners>=0.16.3,<0.18.0',
 'httpx>=0.21.1,<0.22.0',
 'msgpack>=1.0.3,<2.0.0']

setup_kwargs = {
    'name': 'httpx-cache',
    'version': '0.4.1',
    'description': 'Simple caching transport for httpx.',
    'long_description': '# HTTPX-CACHE\n\n[![codecov](https://codecov.io/gh/obendidi/httpx-cache/branch/main/graph/badge.svg?token=FHHRA6F17X)](https://codecov.io/gh/obendidi/httpx-cache)\n\nhttpx-cache is an implementation of the caching algorithms in [httplib2](https://github.com/httplib2/httplib2) and [CacheControl](https://github.com/ionrock/cachecontrol) for use with [httpx](https://github.com/encode/httpx) transport object.\n\nIt is is heavily insipired by:\n\n- [https://github.com/ionrock/cachecontrol](https://github.com/ionrock/cachecontrol)\n- [https://github.com/johtso/httpx-caching](https://github.com/johtso/httpx-caching)\n\n## Documentation\n\nFull documentation is available at [https://obendidi.github.io/httpx-cache/](https://obendidi.github.io/httpx-cache/)\n\n## Installation\n\nUsing pip:\n\n```sh\npip install httpx-cache\n```\n',
    'author': 'Ouail Bendidi',
    'author_email': 'ouail.bendidi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/obendidi/httpx-cache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
