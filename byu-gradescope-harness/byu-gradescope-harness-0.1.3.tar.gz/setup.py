# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['byu_gradescope_harness']
setup_kwargs = {
    'name': 'byu-gradescope-harness',
    'version': '0.1.3',
    'description': 'A test harness for Gradescope autograding',
    'long_description': None,
    'author': 'Gordon Bean',
    'author_email': 'gbean@cs.byu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
