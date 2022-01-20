# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['requirements']

package_data = \
{'': ['*']}

install_requires = \
['types-setuptools>=57.0.0']

setup_kwargs = {
    'name': 'requirements-parser',
    'version': '0.5.0',
    'description': 'This is a small Python module for parsing Pip requirement files.',
    'long_description': "Requirements Parser\n===================\n\n[![Python CI](https://github.com/madpah/requirements-parser/actions/workflows/poetry.yml/badge.svg)](https://github.com/madpah/requirements-parser/actions/workflows/poetry.yml)\n[![Documentation Status](http://readthedocs.org/projects/requirements-parser/badge/?version=latest)](http://requirements-parser.readthedocs.io/en/latest/?badge=latest)\n[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n\nThis is a small Python module for parsing [Pip](http://www.pip-installer.org/) requirement files.\n\nThe goal is to parse everything in the \n[Pip requirement file format](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format) spec.\n\nInstallation\n============\n\n    pip install requirements-parser\n\nor\n\n    poetry add requirements-parser\n\nExamples\n========\n\nRequirements parser can parse a file-like object or a text string.\n\n``` {.python}\n>>> import requirements\n>>> with open('requirements.txt', 'r') as fd:\n...     for req in requirements.parse(fd):\n...         print(req.name, req.specs)\nDjango [('>=', '1.11'), ('<', '1.12')]\nsix [('==', '1.10.0')]\n```\n\nIt can handle most if not all of the options in requirement files that\ndo not involve traversing the local filesystem. These include:\n\n-   editables (`-e git+https://github.com/toastdriven/pyelasticsearch.git]{.title-ref}`)\n-   version control URIs\n-   egg hashes and subdirectories (`[\\#egg=django-haystack&subdirectory=setup]{.title-ref}`)\n-   extras ([DocParser\\[PDF\\]]{.title-ref})\n-   URLs\n\nDocumentation\n=============\n\nFor more details and examples, the documentation is available at:\n<http://requirements-parser.readthedocs.io>.\n\n\nChange Log\n==========\n\nChange log is available on GitHub [here]()\n",
    'author': 'Paul Horton',
    'author_email': 'simplyecommerce@gmail.com',
    'maintainer': 'Paul Horton',
    'maintainer_email': 'simplyecommerce@gmail.com',
    'url': 'https://github.com/madpah/requirements-parser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
