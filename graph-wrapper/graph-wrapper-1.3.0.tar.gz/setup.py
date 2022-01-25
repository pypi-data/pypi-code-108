# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graph', 'graph.retworkx']

package_data = \
{'': ['*']}

install_requires = \
['retworkx>=0.11.0,<0.12.0', 'typing_extensions>=4.0.0,<5.0.0']

setup_kwargs = {
    'name': 'graph-wrapper',
    'version': '1.3.0',
    'description': 'Wrappers of popular network libraries with type annotation',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/binh-vu/graph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
