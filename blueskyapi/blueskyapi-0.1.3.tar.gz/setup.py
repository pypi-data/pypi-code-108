# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['blueskyapi']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.1,<2.0', 'requests>=2.0,<3.0']

setup_kwargs = {
    'name': 'blueskyapi',
    'version': '0.1.3',
    'description': 'Client for blueskyapi.io',
    'long_description': '# python-client\n\nPython client for blueskyapi.io\n\n[![Tests Status](https://github.com/bluesky-api/python-client/workflows/Tests/badge.svg?branch=main&event=push)](https://github.com/bluesky-api/python-client/actions?query=workflow%3ATests+branch%3Amain+event%3Apush)\n[![Coverage Status](https://coveralls.io/repos/github/bluesky-api/python-client/badge.svg?branch=main)](https://coveralls.io/github/bluesky-api/python-client?branch=main)\n[![Stable Version](https://img.shields.io/pypi/v/blueskyapi?label=latest)](https://pypi.org/project/blueskyapi/)\n\n## Installation\n\n`pip install blueskyapi`\n\n## Documentation\n\nThis library is documented [here](https://blueskyapi.readthedocs.io/en/stable/).\n\nFor available variables see the [blueskyapi.io data documentation](https://blueskyapi.io/docs/data).\n',
    'author': 'blueskyapi.io',
    'author_email': 'contact@blueskyapi.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://blueskyapi.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
