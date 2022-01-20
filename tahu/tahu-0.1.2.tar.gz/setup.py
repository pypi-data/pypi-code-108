# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tahu']

package_data = \
{'': ['*']}

install_requires = \
['protobuf==3.19.1']

setup_kwargs = {
    'name': 'tahu',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Aitemir Kuandyk',
    'author_email': 'mooniron.k@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
