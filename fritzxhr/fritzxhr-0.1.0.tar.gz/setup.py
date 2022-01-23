# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['fritzxhr']
install_requires = \
['defusedxml>=0.7.1,<0.8.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'fritzxhr',
    'version': '0.1.0',
    'description': 'An interface to FRITZ!Box web settings',
    'long_description': None,
    'author': 'Andreas Oberritter',
    'author_email': 'obi@saftware.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
