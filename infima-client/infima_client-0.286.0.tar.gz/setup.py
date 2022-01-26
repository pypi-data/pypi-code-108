# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['infima_client',
 'infima_client.api',
 'infima_client.core',
 'infima_client.core.api',
 'infima_client.core.api.cohort_v1',
 'infima_client.core.api.market_v0',
 'infima_client.core.api.pool_v1',
 'infima_client.core.api.prediction_v1',
 'infima_client.core.api.pricing_v0',
 'infima_client.core.api.search_v0',
 'infima_client.core.models',
 'infima_client.core.models.cohort',
 'infima_client.core.models.cohort.v1',
 'infima_client.core.models.core',
 'infima_client.core.models.google',
 'infima_client.core.models.google.protobuf',
 'infima_client.core.models.google.rpc',
 'infima_client.core.models.market',
 'infima_client.core.models.market.v0',
 'infima_client.core.models.mbs',
 'infima_client.core.models.pool',
 'infima_client.core.models.pool.v1',
 'infima_client.core.models.prediction',
 'infima_client.core.models.prediction.v1',
 'infima_client.core.models.prepayment',
 'infima_client.core.models.pricing',
 'infima_client.core.models.pricing.v0',
 'infima_client.core.models.search',
 'infima_client.core.models.search.v0',
 'infima_client.extras']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.1.0,<21.0.0',
 'httpx>=0.15.4,<0.17.0',
 'more-itertools>=8.12.0,<9.0.0',
 'pandas>=1.1.0,<2.0.0',
 'python-dateutil>=2.8.0,<3.0.0',
 'semver>=2.13.0,<3.0.0',
 'stringcase>=1.2.0,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4.2,<5.0',
                                                         'typing_extensions>=4.0.1,<5.0.0']}

setup_kwargs = {
    'name': 'infima-client',
    'version': '0.286.0',
    'description': 'A client library for accessing Infima',
    'long_description': '# infima_client\n\nA client library for accessing Infima. It will manage the HTTP REST requests for you.\n\n## System requirements\n\nThe infima_client requires Python 3.7+. It is multi-platform, and the goal is to make\nit work equally well on Windows, Linux and OSX.\n\n## Installation\n\nThe library is published in PyPi.\n\n```shell\npip install infima_client\n```\n\n## Usage\n\nContact [Support](support@infima.io) for an access token.\n\n```python\nfrom infima_client import InfimaClient\n\ntoken = "..."\nclient = InfimaClient(token=token)\nclient.demo()\n```\n\nAlternatively, the token can be configured with the `INFIMA_TOKEN` environment variable.\n\n## More Information\n\nSee the [Docs](http://docs.infima.io/) for more information.\n\nContact [Support](support@infima.io) if you have any questions.\n',
    'author': 'Alex Papanicolaou',
    'author_email': 'alex@infima.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
