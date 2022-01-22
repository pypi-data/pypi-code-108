# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['bekapoxd']
setup_kwargs = {
    'name': 'bekapoxd',
    'version': '1.0.0',
    'description': 'Package Test!',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
