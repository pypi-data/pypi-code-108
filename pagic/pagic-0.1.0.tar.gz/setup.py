# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pagic', 'tests']

package_data = \
{'': ['*'], 'tests': ['templates/tests/*']}

install_requires = \
['Flask>=2.0.2,<3.0.0', 'venusian>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'pagic',
    'version': '0.1.0',
    'description': 'Top-level package for Pagic.',
    'long_description': '=====\nPagic\n=====\n\n\n.. image:: https://img.shields.io/pypi/v/pagic.svg\n        :target: https://pypi.python.org/pypi/pagic\n\n.. image:: https://img.shields.io/travis/abilian/pagic.svg\n        :target: https://travis-ci.com/abilian/pagic\n\n.. image:: https://readthedocs.org/projects/pagic/badge/?version=latest\n        :target: https://pagic.readthedocs.io/en/latest/?version=latest\n        :alt: Documentation Status\n\n\n\n\nPage-oriented magical web framework.\n\nNot ready for public consumption yet.\n\n\n* Free software: Apache Software License 2.0\n* Documentation: https://pagic.readthedocs.io.\n\n\nFeatures\n--------\n\n* TODO\n\nCredits\n-------\n\nThis package was created with Cruft_ and the `abilian/cookiecutter-abilian-python`_ project template.\n\n.. _Cruft: https://github.com/cruft/cruft\n.. _`abilian/cookiecutter-abilian-python`: https://github.com/abilian/cookiecutter-abilian-python\n',
    'author': 'Abilian SAS',
    'author_email': 'sf@abilian.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abilian/pagic',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
