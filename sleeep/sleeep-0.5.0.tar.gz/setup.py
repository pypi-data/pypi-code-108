# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sleeep']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['sleeep = sleeep.sleeep_main:run']}

setup_kwargs = {
    'name': 'sleeep',
    'version': '0.5.0',
    'description': '',
    'long_description': None,
    'author': 'Steffen Brinkmann',
    'author_email': 's-b@mailbox.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
