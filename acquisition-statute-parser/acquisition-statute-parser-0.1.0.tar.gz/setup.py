# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['acquisition_statute_parser', 'acquisition_statute_parser.elements']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.0.3,<2.0.0',
 'beautifulsoup4>=4.10,<5.0',
 'html-sanitizer>=1.9.3,<2.0.0',
 'html5lib>=1.1,<2.0',
 'httpx>=0.21,<0.22']

setup_kwargs = {
    'name': 'acquisition-statute-parser',
    'version': '0.1.0',
    'description': 'Parse statutes into fields after acquisition from scraping.',
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
