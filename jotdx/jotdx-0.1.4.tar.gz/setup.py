# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jotdx',
 'jotdx.contrib',
 'jotdx.crawler',
 'jotdx.financial',
 'jotdx.parser',
 'jotdx.reader',
 'jotdx.tools',
 'jotdx.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'httpx>=0.20.0,<0.21.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.3.4,<2.0.0',
 'prettytable>=2.2.1,<3.0.0',
 'py-mini-racer>=0.6.0,<0.7.0',
 'tenacity>=8.0.1,<9.0.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'jotdx',
    'version': '0.1.4',
    'description': 'Get data',
    'long_description': None,
    'author': 'FangyangJz',
    'author_email': 'fangyang.jing@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
