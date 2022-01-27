# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['osmflex',
 'osmflex.management',
 'osmflex.management.commands',
 'osmflex.migrations']

package_data = \
{'': ['*'],
 'osmflex.management': ['flex-config/*',
                        'flex-config/layerset/*',
                        'flex-config/sql/*',
                        'flex-config/style/*']}

setup_kwargs = {
    'name': 'osmflex',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Joshua Brooks',
    'author_email': 'josh.vdbroek@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
