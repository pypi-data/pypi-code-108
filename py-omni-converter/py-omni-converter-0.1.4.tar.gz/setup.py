# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omni_converter',
 'omni_converter.auto_data',
 'omni_converter.coconut',
 'omni_converter.solver']

package_data = \
{'': ['*']}

install_requires = \
['cytoolz', 'loguru', 'lru-dict>=1.0.0,<2.0.0', 'pampy', 'tabulate', 'tqdm']

setup_kwargs = {
    'name': 'py-omni-converter',
    'version': '0.1.4',
    'description': '',
    'long_description': None,
    'author': 'Kento Masui',
    'author_email': 'nameissoap@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
