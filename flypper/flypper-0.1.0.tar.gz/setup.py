# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flypper', 'flypper.entities', 'flypper.storage', 'flypper.wsgi']

package_data = \
{'': ['*'], 'flypper.wsgi': ['templates/*']}

modules = \
['README', 'LICENSE']
install_requires = \
['Jinja2>=3.0.0,<4.0.0', 'Werkzeug>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'flypper',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Nicolas Zermati',
    'author_email': 'nicoolas25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
