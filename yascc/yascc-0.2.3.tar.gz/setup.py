# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yascc']

package_data = \
{'': ['*']}

install_requires = \
['setuptools>=60.5.0,<61.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata']}

entry_points = \
{'console_scripts': ['pypi = publish']}

setup_kwargs = {
    'name': 'yascc',
    'version': '0.2.3',
    'description': 'swap cases',
    'long_description': None,
    'author': 'urm8',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
