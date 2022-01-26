# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydapper', 'pydapper.mssql', 'pydapper.postgresql', 'pydapper.sqlite']

package_data = \
{'': ['*']}

install_requires = \
['cached-property>=1.5.2,<2.0.0', 'dsnparse>=0.1.15,<0.2.0']

extras_require = \
{'psycopg2': ['psycopg2-binary>=2.9.2,<3.0.0', 'types-psycopg2>=2.9.4,<3.0.0'],
 'pymssql': ['pymssql>=2.2.3,<3.0.0', 'types-pymssql>=2.1.0,<3.0.0']}

setup_kwargs = {
    'name': 'pydapper',
    'version': '0.1.1a3',
    'description': 'A pure python lib inspired by the dotnet lib dapper',
    'long_description': '[![test](https://github.com/zschumacher/pydapper/actions/workflows/test.yml/badge.svg)](https://github.com/zschumacher/pydapper/actions/workflows/test.yml)\n[![PyPI version](https://badge.fury.io/py/pydapper.svg)](https://badge.fury.io/py/pydapper)\n[![Documentation Status](https://readthedocs.org/projects/pydapper/badge/?version=latest)](https://pydapper.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/zschumacher/pydapper/branch/main/graph/badge.svg?token=3X1IR81HL2)](https://codecov.io/gh/zschumacher/pydapper)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydapper)\n\n# pydapper\nA pure python library inspired by the NuGet library [dapper](https://dapper-tutorial.net).\n\n*pydapper* is built on top of the [dbapi 2.0 spec](https://www.python.org/dev/peps/pep-0249/)\nto provide more convenient methods for working with databases in python.\n\n## Help\nSee the [documentation](https://pydapper.readthedocs.io/en/latest/) for more details.\n\n## Installation\nIt is recommended to only install the database apis you need for your use case.  Example below is for psycopg2!\n```bash\n# pip \npip install pydapper[psycopg2]\n# poetry\npoetry add pydapper -E psycopg2\n```\n\n## A Simple Example\n```python\nfrom dataclasses import dataclass\nimport datetime\n\nfrom pydapper import connect\n\n\n@dataclass\nclass Task:\n    id: int\n    description: str\n    due_date: datetime.date\n\n    \nwith connect("postgresql+psycopg2://pydapper:pydapper@locahost/pydapper") as commands:\n    tasks = commands.query("select id, description, due_date from task;", model=Task)\n    \nprint(tasks)\n# [Task(id=1, description=\'Add a README!\', due_date=datetime.date(2022, 1, 16))]\n```\n(This script is complete, it should run "as is")\n',
    'author': 'Zach Schumacher',
    'author_email': 'zschu15@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<=3.10',
}


setup(**setup_kwargs)
