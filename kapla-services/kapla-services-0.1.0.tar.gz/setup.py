# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kapla',
 'kapla.services',
 'kapla.services.backends',
 'kapla.services.backends.nats',
 'kapla.services.middlewares',
 'kapla.services.middlewares.compression',
 'kapla.services.middlewares.time',
 'kapla.services.testing',
 'kapla.services.utils']

package_data = \
{'': ['*']}

install_requires = \
['Brotli>=1.0.9,<2.0.0',
 'anyio>=3.4.0,<4.0.0',
 'nats-py>=2.0.0-rc.5,<3.0.0',
 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'kapla-services',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'charbonnierg',
    'author_email': 'guillaume.charbonnier@araymond.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
