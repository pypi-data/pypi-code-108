# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['agora', 'agora.io', 'agora.utils', 'logfile_parser']

package_data = \
{'': ['*'],
 'agora': ['data/2019_07_16_aggregates_CTP_switch_2_0glu_0_0glu_URA7young_URA8young_URA8old_01/*',
           'data/2019_07_16_aggregates_CTP_switch_2_0glu_0_0glu_URA7young_URA8young_URA8old_01/2019_07_16_aggregates_CTP_switch_2_0glu_0_0glu_URA7young_URA8young_URA8old_01/*',
           'data/2020_10_22_downUpshift_2_0_2_glu_dual_phluorin__glt1_psa1_ura7__thrice_00/*'],
 'logfile_parser': ['grammars/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'h5py==2.10',
 'opencv-python>=4.5.5,<5.0.0',
 'pandas>=1.3.5,<2.0.0',
 'py-find-1st>=1.1.5,<2.0.0']

setup_kwargs = {
    'name': 'aliby-agora',
    'version': '0.2.10',
    'description': 'A gathering of shared utilities for the Swain Lab image processing pipeline.',
    'long_description': None,
    'author': 'Julian Pietsch',
    'author_email': 'jpietsch@ed.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
