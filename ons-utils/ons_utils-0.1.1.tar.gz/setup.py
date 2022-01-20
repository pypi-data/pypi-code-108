# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ons_utils', 'ons_utils.config', 'ons_utils.pyspark']

package_data = \
{'': ['*']}

install_requires = \
['flatten-dict>=0.4.2,<0.5.0',
 'pandas==1.1.5',
 'pyspark==2.4.1',
 'pyyaml>=6.0,<7.0']

setup_kwargs = {
    'name': 'ons-utils',
    'version': '0.1.1',
    'description': 'A suite of pyspark, pandas and general pipeline utils for ONS projects.',
    'long_description': None,
    'author': 'Mitchell Edmunds',
    'author_email': 'Mitchell.Edmunds@ext.ons.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.8,<3.7.0',
}


setup(**setup_kwargs)
