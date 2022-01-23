# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coretypes', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['deprecation>=2.1.0,<3.0.0', 'numpy>=1.20,<2.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.13.6,<0.14.0',
         'mkdocs-autorefs==0.1.1'],
 'test': ['black==20.8b1',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1']}

setup_kwargs = {
    'name': 'zillionare-core-types',
    'version': '0.2.0',
    'description': 'core types definition shared by zillionare.',
    'long_description': '# zillionare core types\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/zillionare_core_types">\n    <img src="https://img.shields.io/pypi/v/zillionare_core_types.svg"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/zillionare/zillionare_core_types/actions">\n    <img src="https://github.com/zillionare/zillionare_core_types/actions/workflows/main.yml/badge.svg?branch=release" alt="CI Status">\n</a>\n\n<a href="https://zillionare-core-types.readthedocs.io/en/latest/?badge=latest">\n    <img src="https://readthedocs.org/projects/zillionare-core-types/badge/?version=latest" alt="Documentation Status">\n</a>\n\n</p>\n\n\ncore types definition shared by zillionare\n\n\n* Free software: MIT\n* Documentation: <https://zillionare-core-types.readthedocs.io>\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.\n',
    'author': 'Aaron Yang',
    'author_email': 'code@jieyu.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zillionare/zillionare_core_types',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
