# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aliby',
 'aliby.io',
 'aliby.tile',
 'aliby.utils',
 'extraction',
 'extraction.core',
 'extraction.core.functions',
 'extraction.core.functions.custom',
 'extraction.examples']

package_data = \
{'': ['*'],
 'aliby': ['trap_templates/*'],
 'extraction.examples': ['pairs_data/*']}

install_requires = \
['aliby-agora>=0.2.12,<0.3.0',
 'aliby-baby>=0.1.3,<0.2.0',
 'dask>=2021.12.0,<2022.0.0',
 'h5py==2.10',
 'imageio==2.8.0',
 'jaliby-post>=0.1.9,<0.2.0',
 'numpy>=1.16.0,<2.0.0',
 'omero-py>=5.6.2',
 'opencv-python>=4.5.4,<5.0.0',
 'pandas>=1.3.5,<2.0.0',
 'pathos>=0.2.8,<0.3.0',
 'py-find-1st>=1.1.5,<2.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'scikit-image>=0.19.1,<0.20.0',
 'scikit-learn==0.22.2.post1',
 'tqdm>=4.62.3,<5.0.0',
 'zeroc-ice==3.6.5']

setup_kwargs = {
    'name': 'aliby',
    'version': '0.1.15',
    'description': '',
    'long_description': None,
    'author': 'Alan Munoz',
    'author_email': 'alan.munoz@ed.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
