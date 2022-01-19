# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ruuvi_lapio']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'ruuvitag-sensor>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'ruuvi-lapio',
    'version': '0.2.1',
    'description': 'A simple app that sends sensory data over http',
    'long_description': None,
    'author': 'Panu Oksiala',
    'author_email': 'panu@oksiala.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/poksiala/ruuvi-lapio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
