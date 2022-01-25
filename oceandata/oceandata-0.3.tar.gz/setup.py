# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['oceandata', 'oceandata.primary_production']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'numpy>1.14',
 'pandas>1.1',
 'requests>=2.21,<3.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'oceandata',
    'version': '0.3',
    'description': '',
    'long_description': 'None',
    'author': 'Bror Jonsson',
    'author_email': 'brorfred@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
