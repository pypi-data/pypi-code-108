# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['awsmr']
install_requires = \
['awscli>=1.22.41,<2.0.0', 'boto3>=1.20.41,<2.0.0']

entry_points = \
{'console_scripts': ['awsmr = awsmr:main']}

setup_kwargs = {
    'name': 'awsmr',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Iain Samuel McLean Elder',
    'author_email': 'iain@isme.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
