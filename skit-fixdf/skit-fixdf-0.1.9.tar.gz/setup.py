# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skit_fixdf', 'skit_fixdf.fix']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0', 'pandas>=1.3.5,<2.0.0', 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['skit-fixdf = skit_fixdf.cli:main']}

setup_kwargs = {
    'name': 'skit-fixdf',
    'version': '0.1.9',
    'description': "A library to format datasets so that you don't have to.",
    'long_description': None,
    'author': 'ltbringer',
    'author_email': 'amresh.venugopal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/skit-ai/skit-fixdf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
