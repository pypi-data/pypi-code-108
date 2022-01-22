# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esentity']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'esentity',
    'version': '0.2.17',
    'description': 'Elasticsearch Entity Tools',
    'long_description': None,
    'author': 'Slotmarks',
    'author_email': 'info@slotmarks.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://slotmarks.com',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
