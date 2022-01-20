# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['contxt',
 'contxt.auth',
 'contxt.cli',
 'contxt.cli.commands',
 'contxt.models',
 'contxt.services',
 'contxt.utils']

package_data = \
{'': ['*']}

install_requires = \
['auth0-python>=3,<4',
 'click>=7,<8',
 'pyjwt>=1,<2',
 'pyyaml>=5,<7',
 'requests>=2,<3',
 'tabulate']

extras_require = \
{'crypto': ['cryptography>=1.4']}

entry_points = \
{'console_scripts': ['contxt = contxt.__main__:cli']}

setup_kwargs = {
    'name': 'contxt-sdk',
    'version': '2.2.8',
    'description': 'Contxt SDK from ndustrial',
    'long_description': '# Contxt Python SDK\n\n[![CI](https://github.com/ndustrialio/contxt-sdk-python/workflows/CI/badge.svg)](https://github.com/ndustrialio/contxt-sdk-python/actions?query=workflow%3ACI)\n[![pypi version](https://img.shields.io/pypi/v/contxt-sdk.svg)](https://pypi.org/project/contxt-sdk/)\n![python](https://img.shields.io/badge/python-3.7+-blue.svg)\n\n## Installation\n\n```sh\npip install contxt-sdk\n```\n\n## CLI Usage\n\n```sh\ncontxt --help\n```\n\n## Documentation\n\nPlease refer to <https://ndustrialio.github.io/contxt-sdk-python>.\n\n## Contributing\n\nPlease refer to [CONTRIBUTING.md](CONTRIBUTING.md).\n',
    'author': 'ndustrial',
    'author_email': 'dev@ndustrial.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ndustrialio/contxt-sdk-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
