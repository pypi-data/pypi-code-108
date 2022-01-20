# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easy_slurm', 'easy_slurm.templates']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'easy-slurm',
    'version': '0.1.0',
    'description': 'Easily manage and submit robust jobs to Slurm using Python and Bash.',
    'long_description': None,
    'author': 'Mateen Ulhaq',
    'author_email': 'mulhaq2005@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
