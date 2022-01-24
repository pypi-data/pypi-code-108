# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cycparser', 'cycparser.parsing', 'cycparser.repairing']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cycparser',
    'version': '1.0.3',
    'description': '',
    'long_description': None,
    'author': 'Marvin van Aalst',
    'author_email': 'marvin.vanaalst@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
