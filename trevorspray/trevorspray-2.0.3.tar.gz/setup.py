# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trevorspray',
 'trevorspray.lib',
 'trevorspray.lib.enumerators',
 'trevorspray.lib.looters',
 'trevorspray.lib.sprayers']

package_data = \
{'': ['*']}

install_requires = \
['PySocks>=1.7.1,<2.0.0',
 'Pygments>=2.10.0,<3.0.0',
 'exchangelib>=4.6.1,<5.0.0',
 'sh>=1.14.2,<2.0.0',
 'tldextract>=3.1.2,<4.0.0',
 'trevorproxy>=1.0.3,<2.0.0']

entry_points = \
{'console_scripts': ['trevorspray = trevorspray.cli:main']}

setup_kwargs = {
    'name': 'trevorspray',
    'version': '2.0.3',
    'description': 'A modular password sprayer with threading, SSH proxying, loot modules, and more',
    'long_description': None,
    'author': 'TheTechromancer',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/blacklanternsecurity/TREVORspray',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
