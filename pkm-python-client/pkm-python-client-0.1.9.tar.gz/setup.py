# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pkm_python_client']

package_data = \
{'': ['*']}

install_requires = \
['requests']

setup_kwargs = {
    'name': 'pkm-python-client',
    'version': '0.1.9',
    'description': "A python client for the Decoder project's PKM server",
    'long_description': None,
    'author': 'Gaël de Chalendar',
    'author_email': 'gael.de-chalendar@cea.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
