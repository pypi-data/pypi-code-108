# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tutorial_server', 'tutorial_server.static']

package_data = \
{'': ['*']}

install_requires = \
['filetype>=1.0.7,<2.0.0', 'tornado>=6.1,<7.0']

setup_kwargs = {
    'name': 'tutorial-server',
    'version': '1.0.2',
    'description': '',
    'long_description': None,
    'author': 'Mark Hall',
    'author_email': 'mark.hall@open.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
