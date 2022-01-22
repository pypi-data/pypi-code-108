# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['flask_tailwind', 'tests']

package_data = \
{'': ['*'], 'flask_tailwind': ['cruft/*', 'cruft/src/*']}

install_requires = \
['Flask>=2,<3']

entry_points = \
{'flask.commands': ['tailwind = flask_tailwind.cli:tailwind']}

setup_kwargs = {
    'name': 'flask-tailwind',
    'version': '0.1.5',
    'description': 'Flask+Tailwind integration.',
    'long_description': '==============\nFlask-Tailwind\n==============\n\n\n.. image:: https://img.shields.io/pypi/v/flask-tailwind.svg\n        :target: https://pypi.python.org/pypi/flask-tailwind\n\n\nPlugin to simplify use of Tailwind from Flask.\n\n* Status: Alpha. Not documented.\n* Free software: MIT license\n\n\nFeatures\n--------\n\n* TODO\n\nCredits\n-------\n\nThis project is inspired by the `Django-Tailwind`_ project.\n\nThis package was created with `Cookiecutter`_, using the `abilian/cookiecutter-abilian-python`_\nproject template.\n\n.. _`Django-Tailwind`: https://github.com/timonweb/django-tailwind\n.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter\n.. _`abilian/cookiecutter-abilian-python`: https://github.com/abilian/cookiecutter-abilian-python\n',
    'author': 'Abilian SAS',
    'author_email': 'contact@abilian.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abilian/flask-tailwind',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
