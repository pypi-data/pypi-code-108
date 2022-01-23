# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flypper_sqlalchemy', 'flypper_sqlalchemy.storage']

package_data = \
{'': ['*']}

modules = \
['README', 'LICENSE']
install_requires = \
['SQLAlchemy>=1.3,<2.0', 'flypper>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'flypper-sqlalchemy',
    'version': '0.1.1',
    'description': 'Feature flags, with a GUI - SQL Alchemy backend',
    'long_description': None,
    'author': 'Nicolas Zermati',
    'author_email': 'nicoolas25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nicoolas25/flypper-sqlalchemy',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
