# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['servicex_did_finder_lib']

package_data = \
{'': ['*']}

install_requires = \
['make-it-sync>=1.0.0,<2.0.0', 'pika==1.1.0', 'requests>=2.25.0,<3.0.0']

setup_kwargs = {
    'name': 'servicex-did-finder-lib',
    'version': '1.0.2',
    'description': 'ServiceX DID Library Routines',
    'long_description': None,
    'author': 'Gordon Watts',
    'author_email': 'gwatts@uw.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
