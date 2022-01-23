# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bamboo_engine',
 'bamboo_engine.builder',
 'bamboo_engine.builder.flow',
 'bamboo_engine.eri',
 'bamboo_engine.handlers',
 'bamboo_engine.template',
 'bamboo_engine.utils',
 'bamboo_engine.utils.boolrule',
 'bamboo_engine.utils.mako_utils',
 'bamboo_engine.validator']

package_data = \
{'': ['*']}

install_requires = \
['Mako>=1.1.4,<2.0.0',
 'Werkzeug>=1.0.0,<2.0.0',
 'prometheus-client>=0.9.0,<0.10.0',
 'pyparsing>=2.2.0,<3.0.0']

setup_kwargs = {
    'name': 'bamboo-engine',
    'version': '1.6.3',
    'description': 'Bamboo-engine is a general-purpose workflow engine',
    'long_description': None,
    'author': 'homholueng',
    'author_email': 'homholueng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.8',
}


setup(**setup_kwargs)
