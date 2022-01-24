# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stonecharioteer', 'stonecharioteer.qtile', 'stonecharioteer.utils']

package_data = \
{'': ['*']}

install_requires = \
['mypy>=0.910,<0.911',
 'psutil>=5.8.0,<6.0.0',
 'python-xlib>=0.31,<0.32',
 'qtile>=0.18.1,<0.19.0',
 'requests>=2.26.0,<3.0.0',
 'rich>=10.12.0,<11.0.0',
 'toml>=0.10.2,<0.11.0',
 'types-toml>=0.10.1,<0.11.0']

setup_kwargs = {
    'name': 'stonecharioteer',
    'version': '0.3.4',
    'description': 'My personal utils and configs, managed via python library',
    'long_description': None,
    'author': 'Vinay Keerthi',
    'author_email': '11478411+stonecharioteer@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
