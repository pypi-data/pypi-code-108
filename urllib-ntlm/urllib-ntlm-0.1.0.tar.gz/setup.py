# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ntlm']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'urllib-ntlm',
    'version': '0.1.0',
    'description': 'NTLM Authenticator for urllib.request',
    'long_description': None,
    'author': 'Martin Ortbauer',
    'author_email': 'mortbauer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mortbauer/urllib-ntlm',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
