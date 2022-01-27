# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['recap_utils']

package_data = \
{'': ['*']}

install_requires = \
['arg-services>=0.1.18,<0.2.0',
 'arguebuf>=0.2.3,<0.3.0',
 'deepl-pro>=0.1.4,<0.2.0',
 'tomlkit>=0.7,<0.8',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['recap-utils = recap_utils.app:cli']}

setup_kwargs = {
    'name': 'recap-utils',
    'version': '0.2.1',
    'description': '',
    'long_description': None,
    'author': 'Mirko Lenz',
    'author_email': 'info@mirko-lenz.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
