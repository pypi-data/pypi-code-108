# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_pep585']

package_data = \
{'': ['*']}

entry_points = \
{'flake8.extension': ['PEA = flake8_pep585.plugin:Pep585Plugin']}

setup_kwargs = {
    'name': 'flake8-pep585',
    'version': '0.1.1',
    'description': 'flake8 plugin to enforce new-style type hints (PEP 585)',
    'long_description': None,
    'author': 'decorator-factory',
    'author_email': 'decorator-factory@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
