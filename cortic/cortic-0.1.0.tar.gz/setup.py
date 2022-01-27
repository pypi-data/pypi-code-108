# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cortic']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'mlflow>=1.23.1,<2.0.0']

entry_points = \
{'console_scripts': ['cortic = cortic.cli:cli']}

setup_kwargs = {
    'name': 'cortic',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Seth Juarez',
    'author_email': None,
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
