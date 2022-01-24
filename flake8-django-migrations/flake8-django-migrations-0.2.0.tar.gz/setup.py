# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_django_migrations', 'flake8_django_migrations.checkers']

package_data = \
{'': ['*']}

install_requires = \
['astor>=0.1', 'flake8>=3.7']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=0.9']}

entry_points = \
{'flake8.extension': ['DM = flake8_django_migrations:Plugin']}

setup_kwargs = {
    'name': 'flake8-django-migrations',
    'version': '0.2.0',
    'description': 'Flake8 plugin to lint for backwards incompatible database migrations',
    'long_description': '# flake8-django-migrations\n\n<p align="center">\n  <a href="https://github.com/browniebroke/flake8-django-migrations/actions?query=workflow%3ACI">\n    <img alt="CI Status" src="https://img.shields.io/github/workflow/status/browniebroke/flake8-django-migrations/CI?label=CI&logo=github&style=flat-square">\n  </a>\n  <a href="https://codecov.io/gh/browniebroke/flake8-django-migrations">\n    <img src="https://img.shields.io/codecov/c/github/browniebroke/flake8-django-migrations.svg?logo=codecov&style=flat-square" alt="Test coverage percentage">\n  </a>\n</p>\n<p align="center">\n  <a href="https://python-poetry.org/">\n    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">\n  </a>\n  <a href="https://github.com/ambv/black">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">\n  </a>\n  <a href="https://github.com/pre-commit/pre-commit">\n    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">\n  </a>\n</p>\n<p align="center">\n  <a href="https://pypi.org/project/flake8-django-migrations/">\n    <img src="https://img.shields.io/pypi/v/flake8-django-migrations.svg?logo=python&amp;logoColor=fff&amp;style=flat-square" alt="PyPi Status">\n  </a>\n  <img src="https://img.shields.io/pypi/pyversions/flake8-django-migrations.svg?style=flat-square" alt="pyversions">\n  <img src="https://img.shields.io/pypi/l/flake8-django-migrations.svg?style=flat-square" alt="license">\n</p>\n\nFlake8 plugin to lint for backwards incompatible database migrations.\n\n## Installation\n\nInstall using `pip` (or your favourite package manager):\n\n```sh\npip install flake8-django-migrations\n```\n\n## Usage\n\nThis plugin should be used automatically when running flake8:\n\n```sh\nflake8\n```\n\n\n## Checks\n\nThis is the list of checks currently implemented by this plugin.\n\n### DM001\n\n`RemoveField` operation should be wrapped in `SeparateDatabaseAndState`.\n\nSuch an operation should be run in two separate steps, using `SeparateDatabaseAndState`, otherwise it is not backwards compatible.\n\n* Step 1: remove the field from the model and code. For foreign key fields, the foreign key constraint should also be dropped.\n* Step 2: remove the column from the database.\n\n#### Bad\n\n```python\nclass Migration(migrations.Migration):\n    operations = [\n        migrations.RemoveField(\n            model_name="order",\n            name="total",\n        ),\n    ]\n```\n\n#### Good\n\n```python\nclass Migration(migrations.Migration):\n    operations = [\n        migrations.SeparateDatabaseAndState(\n            state_operations=[\n                migrations.RemoveField(\n                    model_name="order",\n                    name="total",\n                ),\n            ],\n        ),\n    ]\n```\n',
    'author': 'Bruno Alla',
    'author_email': 'bruno.alla@festicket.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/browniebroke/flake8-django-migrations',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
