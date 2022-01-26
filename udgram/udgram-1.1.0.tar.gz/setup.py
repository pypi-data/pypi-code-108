# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['udgram']
install_requires = \
['conllu==4.4.1']

setup_kwargs = {
    'name': 'udgram',
    'version': '1.1.0',
    'description': '',
    'long_description': None,
    'author': 'wellington36',
    'author_email': 'wellington.71319@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>3.8',
}


setup(**setup_kwargs)
