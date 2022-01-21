# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sqla2uml', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4,<2.0']

entry_points = \
{'console_scripts': ['sqla2uml = sqla2uml.main:main']}

setup_kwargs = {
    'name': 'sqla2uml',
    'version': '0.1.0.post1',
    'description': 'Top-level package for SqlAlchemy2UML.',
    'long_description': '==============\nSqlAlchemy2UML\n==============\n\n\n.. image:: https://img.shields.io/pypi/v/sqla2uml.svg\n        :target: https://pypi.python.org/pypi/sqla2uml\n\n.. image:: https://img.shields.io/travis/sfermigier/sqla2uml.svg\n        :target: https://travis-ci.com/sfermigier/sqla2uml\n\n.. image:: https://readthedocs.org/projects/sqla2uml/badge/?version=latest\n        :target: https://sqla2uml.readthedocs.io/en/latest/?version=latest\n        :alt: Documentation Status\n\n\n\nUsage\n-----\n\nInstall as a development dependency in your project, then type `sqla2uml` for help::\n\n    Usage: sqla2uml [OPTIONS]\n\n    Options:\n      -m, --module TEXT          Package to analyse (recursively)\n      -o, --output TEXT          File to output result (defaults to stdout)\n      -p, --properties BOOLEAN   Include properties in diagrams\n      -x, --exclude TEXT         List of class names to exclude from diagram\n      -d, --debug-level INTEGER  Debug level\n      --help                     Show this message and exit.\n\n\n* Free software: MIT license\n* Documentation: https://sqla2uml.readthedocs.io. (not working yet)\n\n\nFeatures\n--------\n\n* Generate UML diagrams from SQLAlchemy models.\n* One must have PlantUML installed.\n* More features / more flexibility to come later.\n\n\nDevelopment\n-----------\n\n* Pull-requests accepted.\n* Participants must adhere to the Python COC (<https://www.python.org/psf/>)\n\n\nCredits\n-------\n\nThis package was created with Cruft_ and the `abilian/cookiecutter-abilian-python`_ project template.\n\n.. _Cruft: https://github.com/cruft/cruft\n.. _`abilian/cookiecutter-abilian-python`: https://github.com/abilian/cookiecutter-abilian-python\n',
    'author': 'Abilian SAS',
    'author_email': 'sf@abilian.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sfermigier/sqla2uml',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
