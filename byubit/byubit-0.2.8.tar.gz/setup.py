# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['byubit']
install_requires = \
['matplotlib>=3.5.1,<4.0.0', 'numpy>=1.22.0,<2.0.0']

setup_kwargs = {
    'name': 'byubit',
    'version': '0.2.8',
    'description': 'A library for teaching beginners how to program',
    'long_description': None,
    'author': 'Gordon Bean',
    'author_email': 'gbean@cs.byu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
