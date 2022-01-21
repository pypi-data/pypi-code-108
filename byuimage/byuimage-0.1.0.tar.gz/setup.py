# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['byuimage']
install_requires = \
['Pillow-PIL>=0.1dev,<0.2']

setup_kwargs = {
    'name': 'byuimage',
    'version': '0.1.0',
    'description': 'Simple Image processing library, used for teaching people how to program',
    'long_description': None,
    'author': 'Daniel Zappala',
    'author_email': 'daniel.zappala@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
