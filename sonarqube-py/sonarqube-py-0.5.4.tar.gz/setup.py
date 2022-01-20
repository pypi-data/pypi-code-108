# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sonarqube']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'click>=8.0.3,<9.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'sonarqube-py',
    'version': '0.5.4',
    'description': 'A python wrapper for the SonarQube web API',
    'long_description': None,
    'author': 'Pat',
    'author_email': 'itchyknee@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yantantether/sonarqube-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
