# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['agam_conservation']

package_data = \
{'': ['*']}

install_requires = \
['h5py', 'humanize', 'numpy', 'pandas', 'requests', 'scikit-allel', 'seaborn']

setup_kwargs = {
    'name': 'agam-conservation',
    'version': '0.2.1',
    'description': '',
    'long_description': None,
    'author': 'Nace Kranjc',
    'author_email': 'nkranjc@ic.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
