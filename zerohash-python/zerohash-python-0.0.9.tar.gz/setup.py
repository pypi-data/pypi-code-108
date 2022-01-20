# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zerohash', 'zerohash.resources', 'zerohash.resources.abstract']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'zerohash-python',
    'version': '0.0.9',
    'description': 'Python library for the Zero Hash API',
    'long_description': None,
    'author': 'Crawford Leeds',
    'author_email': 'crawford@getlinus.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
