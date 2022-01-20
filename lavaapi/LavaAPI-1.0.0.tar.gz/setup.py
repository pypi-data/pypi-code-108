# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['lavaapi']
setup_kwargs = {
    'name': 'lavaapi',
    'version': '1.0.0',
    'description': 'A simple library for accepting payments and using the LAVA Wallet',
    'long_description': None,
    'author': 'billiedark',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
