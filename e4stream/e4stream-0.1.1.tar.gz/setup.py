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
    'version': '0.1.1',
    'description': 'Python package that provides a simple API for interacting with packets coming from the Empatica E4 Streaming Server',
    'long_description': '# e4stream\n`e4stream` is a Python package that provides a simple client-side API for interacting with the E4 Streaming Server for the Empatica E4 device.\n',
    'author': 'Jason Raether',
    'author_email': 'jasondraether@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jasondraether/e4stream',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
