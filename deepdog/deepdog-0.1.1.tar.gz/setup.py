# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepdog']

package_data = \
{'': ['*']}

install_requires = \
['pdme>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'deepdog',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Deepak Mallubhotla',
    'author_email': 'dmallubhotla+github@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
