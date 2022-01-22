# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rapidhrv']

package_data = \
{'': ['*']}

install_requires = \
['dash>=2.0.0,<3.0.0',
 'h5py>=3.3.0,<4.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.7.0,<2.0.0']

extras_require = \
{'notebooks': ['jupyter>=1.0.0,<2.0.0', 'matplotlib>=3.4.2,<4.0.0']}

setup_kwargs = {
    'name': 'rapidhrv',
    'version': '0.2.1',
    'description': 'A package for preprocessing, analyzing and visualizing cardiac data',
    'long_description': None,
    'author': 'Peter Kirk',
    'author_email': 'p.kirk@ucl.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
