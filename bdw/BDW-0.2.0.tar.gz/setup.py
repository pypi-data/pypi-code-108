# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bdw', 'bdw.ext']

package_data = \
{'': ['*']}

install_requires = \
['websocket-client==1.2.1']

setup_kwargs = {
    'name': 'bdw',
    'version': '0.2.0',
    'description': 'A bad discord wrapper for python.',
    'long_description': None,
    'author': 'Fox551',
    'author_email': 'BadPythonCoder@TheInternet.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
