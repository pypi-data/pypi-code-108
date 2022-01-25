# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['solsim']

package_data = \
{'': ['*']}

install_requires = \
['anchorpy>=0.6.4,<0.7.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.4.0,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'solsim',
    'version': '0.1.0',
    'description': 'The Solana complex systems simulator.',
    'long_description': None,
    'author': 'Will Wolf',
    'author_email': 'williamabrwolf@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
