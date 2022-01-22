# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['acquisition_sanitizer']

package_data = \
{'': ['*']}

install_requires = \
['html-sanitizer>=1.9.3,<2.0.0']

setup_kwargs = {
    'name': 'acquisition-sanitizer',
    'version': '0.2.0',
    'description': 'Clean scraped decisions for better pattern matching.',
    'long_description': None,
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
