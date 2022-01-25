# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mmf_meta']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'pydantic>=1.9.0,<2.0.0']

entry_points = \
{'console_scripts': ['mmfmeta = mmf_meta:cli']}

setup_kwargs = {
    'name': 'mmf-meta',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Викторов Андрей Германович',
    'author_email': 'andvikt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
