# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['message_db']

package_data = \
{'': ['*']}

install_requires = \
['psycopg2>=2.9.2,<3.0.0']

setup_kwargs = {
    'name': 'message-db-py',
    'version': '0.1.2',
    'description': 'The Python interface to the MessageDB Event Store and Message Store',
    'long_description': None,
    'author': 'Subhash Bhushan',
    'author_email': 'subhash.bhushan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
