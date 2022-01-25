# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['steiner_tree', 'steiner_tree.bank']

package_data = \
{'': ['*']}

install_requires = \
['graph-wrapper>=1.3.0,<1.4.0', 'networkx>=2.6.3,<3.0.0']

setup_kwargs = {
    'name': 'steiner-tree',
    'version': '1.1.0',
    'description': 'Steiner Tree algorithms',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/binh-vu/steiner-tree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
