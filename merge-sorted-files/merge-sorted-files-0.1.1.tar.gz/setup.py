# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['merge_sorted_files']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['merge-sorted-files = merge_sorted_files.main:main']}

setup_kwargs = {
    'name': 'merge-sorted-files',
    'version': '0.1.1',
    'description': 'Merge sorted files and write output to disk',
    'long_description': None,
    'author': 'Ilia Krets',
    'author_email': 'mrchair2170@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
