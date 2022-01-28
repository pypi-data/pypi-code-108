# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['desdeo_tools',
 'desdeo_tools.interaction',
 'desdeo_tools.maps',
 'desdeo_tools.scalarization',
 'desdeo_tools.solver',
 'desdeo_tools.utilities']

package_data = \
{'': ['*']}

install_requires = \
['hvwfg>=1.0.2,<2.0.0',
 'numba>=0.53.1,<0.54.0',
 'numpy>=1.17,<2.0',
 'pandas>=1.0,<2.0',
 'scipy>=1.2,<2.0']

setup_kwargs = {
    'name': 'desdeo-tools',
    'version': '1.6.0',
    'description': 'Generic tools and design language used in the DESDEO framework',
    'long_description': None,
    'author': 'Bhupinder Saini',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
