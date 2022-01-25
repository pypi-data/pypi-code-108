# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nebari']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nebari',
    'version': '0.0.1',
    'description': 'Nebari',
    'long_description': '# Nebari\n\nStay tuned!\n',
    'author': 'Quansight',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/quansight/nebari',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
