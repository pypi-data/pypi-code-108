# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['e4stream']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'e4stream',
    'version': '0.1.0',
    'description': 'Python package that provides a simple API for interacting with packets coming from the Empatica E4 Streaming Server',
    'long_description': None,
    'author': 'Jason Raether',
    'author_email': 'jasondraether@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
