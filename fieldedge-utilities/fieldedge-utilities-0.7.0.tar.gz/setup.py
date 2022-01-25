# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fieldedge_utilities']

package_data = \
{'': ['*']}

install_requires = \
['paho-mqtt>=1.6.1,<2.0.0',
 'pyserial>=3.5,<4.0',
 'python-dotenv>=0.19.1,<0.20.0']

setup_kwargs = {
    'name': 'fieldedge-utilities',
    'version': '0.7.0',
    'description': 'Utilities package for the FieldEdge project.',
    'long_description': '# Inmarsat FieldEdge Utilities\n\nInmarsat FieldEdge project supports *Internet of Things* (**IoT**) using\nsatellite communications technology.\n\nThis library available on **PyPI** provides:\n\n* A common **`logger`** format and wrapping file facility.\n* A simplified **`mqtt`** client that automatically connects\n(to a `fieldedge-broker`).\n* Helper functions for managing files and **`path`** on different OS.\n* An interface for **`hostpipe`** service interacting via a logfile.\n\n[Docmentation](https://inmarsat-enterprise.github.io/fieldedge-utilities/)\n',
    'author': 'geoffbrucepayne',
    'author_email': 'geoff.bruce-payne@inmarsat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inmarsat-enterprise/fieldedge-utilities',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
