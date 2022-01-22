# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cpenv',
 'cpenv.cli',
 'cpenv.repos',
 'cpenv.vendor',
 'cpenv.vendor.cachetools',
 'cpenv.vendor.certifi',
 'cpenv.vendor.shotgun_api3',
 'cpenv.vendor.shotgun_api3.lib',
 'cpenv.vendor.shotgun_api3.lib.certifi',
 'cpenv.vendor.shotgun_api3.lib.httplib2',
 'cpenv.vendor.shotgun_api3.lib.httplib2.python2',
 'cpenv.vendor.shotgun_api3.lib.httplib2.python3',
 'cpenv.vendor.shotgun_api3.lib.mockgun',
 'cpenv.vendor.yaml',
 'cpenv.vendor.yaml.yaml2',
 'cpenv.vendor.yaml.yaml3']

package_data = \
{'': ['*'], 'cpenv': ['bin/*']}

install_requires = \
['colorama>=0.4.3,<0.5.0', 'psutil>=5.7.0,<6.0.0', 'tqdm>=4.46.0,<5.0.0']

entry_points = \
{'console_scripts': ['cpenv = cpenv.__main__:main']}

setup_kwargs = {
    'name': 'cpenv',
    'version': '0.5.27',
    'description': 'Cross-platform module and environment management.',
    'long_description': None,
    'author': 'Dan Bradham',
    'author_email': 'danielbradham@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
