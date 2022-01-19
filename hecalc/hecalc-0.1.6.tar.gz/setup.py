# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hecalc', 'hecalc.GUI']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18.1',
 'openpyxl>=3.0.3',
 'pandas>=1.0.3',
 'scipy>=1.4.1',
 'setuptools>=41.2.0']

extras_require = \
{'GUI': ['PyQt5>=5.15.6,<6.0.0',
         'tabulate>=0.8.9,<0.9.0',
         'xlrd>=1.2.0,<2.0.0']}

setup_kwargs = {
    'name': 'hecalc',
    'version': '0.1.6',
    'description': 'A tool for performing (U-Th)/He data reduction and uncertainty propagation',
    'long_description': None,
    'author': 'Peter E. Martin',
    'author_email': 'peter.martin-2@colorado.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
