# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bungieapi',
 'bungieapi.generated',
 'bungieapi.generated.clients',
 'bungieapi.generated.components',
 'bungieapi.generated.components.responses',
 'bungieapi.generated.components.responses.common',
 'bungieapi.generated.components.responses.config',
 'bungieapi.generated.components.responses.content',
 'bungieapi.generated.components.responses.destiny',
 'bungieapi.generated.components.responses.social',
 'bungieapi.generated.components.schemas',
 'bungieapi.generated.components.schemas.common',
 'bungieapi.generated.components.schemas.config',
 'bungieapi.generated.components.schemas.content',
 'bungieapi.generated.components.schemas.destiny',
 'bungieapi.generated.components.schemas.destiny.components',
 'bungieapi.generated.components.schemas.destiny.definitions',
 'bungieapi.generated.components.schemas.destiny.entities',
 'bungieapi.generated.components.schemas.destiny.historical_stats',
 'bungieapi.generated.components.schemas.destiny.reporting',
 'bungieapi.generated.components.schemas.destiny.requests',
 'bungieapi.generated.components.schemas.social',
 'bungieapi.generated.components.schemas.tags',
 'bungieapi.generated.components.schemas.tags.models',
 'bungieapi.generated.components.schemas.user']

package_data = \
{'': ['*'], 'bungieapi': ['certs/*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'svarog>=0.2.2,<0.3.0']

setup_kwargs = {
    'name': 'bungieapi',
    'version': '0.0.4',
    'description': 'Python client for bungie api',
    'long_description': None,
    'author': 'Damian Świstowski',
    'author_email': 'damian@swistowski.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
