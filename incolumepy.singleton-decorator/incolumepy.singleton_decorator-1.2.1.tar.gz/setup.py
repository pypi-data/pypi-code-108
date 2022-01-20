# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['singleton_decorator']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'incolumepy.singleton-decorator',
    'version': '1.2.1',
    'description': '',
    'long_description': None,
    'author': 'Britodfbr',
    'author_email': 'britodfbr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
