# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['maaml',
 'maaml.Datasets',
 'maaml.Datasets.UAH_dataset',
 'maaml.functions',
 'maaml.functions.Datasets']

package_data = \
{'': ['*'], 'maaml.Datasets.UAH_dataset': ['dataset/*']}

install_requires = \
['keras>=2.7,<3.0',
 'matplotlib>=3.4,<4.0',
 'numpy>=1.22.0,<2.0.0',
 'pandas>=1.3,<2.0',
 'sklearn>=0.0,<0.1']

setup_kwargs = {
    'name': 'maaml',
    'version': '0.3.1',
    'description': 'For time series datasets Machine learning pipline',
    'long_description': None,
    'author': 'Najemeddine Abdennour',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
