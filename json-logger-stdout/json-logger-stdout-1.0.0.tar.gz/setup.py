# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json-logger-stdout']

package_data = \
{'': ['*']}

install_requires = \
['python-json-logger>=2.0.2,<3.0.0']

setup_kwargs = {
    'name': 'json-logger-stdout',
    'version': '1.0.0',
    'description': 'JSON Logger for MicroServices. Prints logs to the stdout of the service and can be shipped to ES by leveraging a centralized tool like Fluentd',
    'long_description': None,
    'author': 'Chalukya J',
    'author_email': 'chalukya@sentieo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
