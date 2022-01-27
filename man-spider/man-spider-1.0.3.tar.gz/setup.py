# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['man_spider', 'man_spider.lib', 'man_spider.lib.parser']

package_data = \
{'': ['*'], 'man_spider': ['logs/*', 'loot/*']}

install_requires = \
['impacket>=0.9.22,<0.10.0',
 'python-magic>=0.4.22,<0.5.0',
 'textract>=1.6.3,<2.0.0']

entry_points = \
{'console_scripts': ['manspider = man_spider.manspider:main']}

setup_kwargs = {
    'name': 'man-spider',
    'version': '1.0.3',
    'description': 'Full-featured SMB spider capable of searching file content',
    'long_description': None,
    'author': 'TheTechromancer',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/blacklanternsecurity/MANSPIDER',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
