# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fakts',
 'fakts.beacon',
 'fakts.cli',
 'fakts.config',
 'fakts.grants',
 'fakts.grants.cli',
 'fakts.grants.meta',
 'fakts.grants.qt',
 'fakts.middleware',
 'fakts.middleware.environment']

package_data = \
{'': ['*'], 'fakts': ['assets/*']}

install_requires = \
['PyYAML>=5.2',
 'QtPy>=1.11.2,<2.0.0',
 'koil>=0.1.59,<0.2.0',
 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'fakts',
    'version': '0.1.40',
    'description': 'asynchronous configuration protocol for dynamic client-server relations',
    'long_description': '# fakts\n\n[![codecov](https://codecov.io/gh/jhnnsrs/fakts/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/fakts)\n[![PyPI version](https://badge.fury.io/py/fakts.svg)](https://pypi.org/project/fakts/)\n[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/fakts/)\n![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/fakts.svg)](https://pypi.python.org/pypi/fakts/)\n[![PyPI status](https://img.shields.io/pypi/status/fakts.svg)](https://pypi.python.org/pypi/fakts/)\n[![PyPI download day](https://img.shields.io/pypi/dm/fakts.svg)](https://pypi.python.org/pypi/fakts/)\n\n### DEVELOPMENT\n\n## Inspiration\n\nFakts tries to make the setup process between client - dynamic server relations as easy as possible.\n\n## Client - Dynamic Server\n\nIn this relation the configuration of the server is unbeknownst to the client, that means which network\naddress it can connect to retrieve its initial configuration. As both client and server need to trust\neach other this is a complex scenario to secure. Therefore fakts provided different grants to ensure different\nlevels of security.\n\n## Simple grant\n\nIn the fakts grants, fakts simply advertises itself on the network through UDP broadcasts and sends standardized configuration\nto the client. In this scenario no specific configuration on a per app basis is possible, as every client that chooses to connect to the\nserver will receive the same configuration.\n\n### Server\n\n```bash\nfakts serve fakts.yaml\n```\n\n### Client\n\n```bash\nfakts init\n```\n\nThis flow however can be secured by a password that needs to be entered, once the client wants to retrieve configuration.\n\n### Server\n\n```bash\nfakts serve fakts.yaml --password="*******"\n```\n\n## Advanced grant\n\nIn an oauth2 redirect like manner, fakts can also be used to advocate an endpoint that the app can then connect to in order to receive\nspecialised configuration through a redirect back to the client.\n\n### Beacon\n\n```bash\nfakts beacon "http://localhost:3000/beacon"\n```\n\n### Client\n\n```bash\nfakts init --client="napari"\n```\n\nIn this scenario the client will open a webbrowser with the query parameters set to the init params (in addition to a state to combat redirect attacks, and a redirect_uri) and\nwait for a redirect to its redirect_uri on localhost with the configuration in the query params\n',
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
