# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['disfs']

package_data = \
{'': ['*']}

install_requires = \
['config-path>=1.0.2,<2.0.0',
 'keyring>=21.2.0,<22.0.0',
 'pycryptodome>=3.12.0,<4.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.27.1,<3.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['disfs = disfs.cli:main']}

setup_kwargs = {
    'name': 'disfs',
    'version': '0.1.1',
    'description': 'Discord-based filesystem',
    'long_description': None,
    'author': 'witherornot',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
