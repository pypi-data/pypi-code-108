# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dcarte', 'dcarte.derived', 'dcarte.legacy']

package_data = \
{'': ['*'], 'dcarte': ['source_yaml/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'deepdiff>=5.7.0,<6.0.0',
 'numpy>=1.19.5',
 'pandas>=1.3.4',
 'pyarrow>=3.0.0,<6.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.26.0,<3.0.0',
 'scipy>=1.7.3,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'dcarte',
    'version': '0.3.15',
    'description': 'DCARTE is a dataset ingestion tool from DCARTE UK-DRI CAre Research and TEchnology',
    'long_description': None,
    'author': 'eyal soreq',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/esoreq/dcarte',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
