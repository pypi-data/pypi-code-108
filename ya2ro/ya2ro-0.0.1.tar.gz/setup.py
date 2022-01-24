# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ya2ro']
install_requires = \
['PyYAML>=6.0,<7.0',
 'Pygments>=2.11.2,<3.0.0',
 'bibtexparser>=1.2.0,<2.0.0',
 'bs4>=0.0.1,<0.0.2',
 'requests>=2.27.1,<3.0.0',
 'somef>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'ya2ro',
    'version': '0.0.1',
    'description': 'Human and machine readable input as a yaml file and create RO-Object in jsonld and/or HTML',
    'long_description': None,
    'author': 'view.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
