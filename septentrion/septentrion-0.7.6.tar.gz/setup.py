# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['septentrion']

package_data = \
{'': ['*']}

install_requires = \
['click', 'colorama', 'importlib-metadata', 'sqlparse']

extras_require = \
{'psycopg2': ['psycopg2'], 'psycopg2_binary': ['psycopg2_binary']}

entry_points = \
{'console_scripts': ['septentrion = septentrion.__main__:main']}

setup_kwargs = {
    'name': 'septentrion',
    'version': '0.7.6',
    'description': 'Python CLI tool for managing and executing hand-written PostgreSQL migrations',
    'long_description': "Septentrion: A CLI tool to apply PostgreSQL migrations to a database\n====================================================================\n\n.. image:: https://badge.fury.io/py/septentrion.svg\n    :target: https://pypi.org/pypi/septentrion\n    :alt: Deployed to PyPI\n\n.. image:: https://readthedocs.org/projects/septentrion/badge/?version=latest\n    :target: http://septentrion.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\n.. image:: https://img.shields.io/github/workflow/status/peopledoc/septentrion/CI?logo=github\n    :target: https://github.com/peopledoc/septentrion/actions?workflow=CI\n    :alt: Continuous Integration Status\n\n.. image:: https://codecov.io/gh/peopledoc/septentrion/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/peopledoc/septentrion\n    :alt: Coverage Status\n\n.. image:: https://img.shields.io/badge/License-MIT-green.svg\n    :target: https://github.com/peopledoc/septentrion/blob/master/LICENSE\n    :alt: MIT License\n\n.. image:: https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg\n    :target: CODE_OF_CONDUCT.md\n    :alt: Contributor Covenant\n\nOverview\n--------\n\nMaybe you're looking for a tool to take care of Database migrations in your project. For\nDjango projects, that tool used to be South_ and then it became Django\nitself.\n\nBut maybe you're looking for a tool that just focuses on running existing SQL migrations\nand keeping track of what was applied. Your tool of choice would not generate those\nmigrations, because you prefer your migrations to be manually written in SQL. Then your\ntool would be django-north_.\n\nBut maybe you're not using Django. You would like a standalone migration tool. You're\nlooking for Septentrion. Congratulations, you've found it.\n\nSeptentrion supports PostgreSQL 9.6+ & Python 3.7+, and requires the ``psql``\nexecutable to be present on the system.\n\n.. _South: https://bitbucket.org/andrewgodwin/south/src\n.. _django-north: https://github.com/peopledoc/django-north\n\nVery quick start\n----------------\n\n- *Step 0*: Install with ``pip install septentrion[psycopg2_binary]`` (or\n  ``pip install septentrion[psycopg2]`` if you know what you're doing)\n\n- *Step 1*: Create a folder for the version, and add some migration files.\n\n.. code-block:: console\n\n    migrations/\n    └──  1.0\n      \xa0 ├── 1.0-0-version-dml.sql\n     \xa0\xa0 ├── 1.0-author-1-ddl.sql\n     \xa0\xa0 └── 1.0-author-2-dml.sql\n\n- *Step 2*: Run septentrion\n\n.. code-block:: console\n\n    $ septentrion --target-version 1.0 migrate\n\n- *Step 3*: That's it.\n\n.. Below this line is content specific to the README that will not appear in the doc.\n.. end-of-index-doc\n\nWe're currently working on this tool, and it's been used internally since 2018, but\nfor now, if you want to use it without a direct access to the people who\nwrote it, you're going to have a lot of questions. We expect a proper documentation\nto be ready by mid-2020. Please feel free to contact us meanwhile.\n\nWhere to go from here\n---------------------\n\nThe complete docs_ is probably the best place to learn about the project.\n\nYou can check the quickstart_ guide to start running your first migrations.\n\nIf you encounter a bug, or want to get in touch, you're always welcome to open a\nticket_.\n\n.. _docs: http://septentrion.readthedocs.io/en/latest\n.. _quickstart: http://septentrion.readthedocs.io/en/latest/quickstart.html\n.. _ticket: https://github.com/peopledoc/septentrion/issues/new\n",
    'author': 'Python UKG Community',
    'author_email': 'peopledoc-python@ukg.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://septentrion.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
