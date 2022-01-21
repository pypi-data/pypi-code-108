# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jsonvice']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['jsonvice = jsonvice.jsonvice:cli']}

setup_kwargs = {
    'name': 'jsonvice',
    'version': '0.1.1',
    'description': 'Simply CLI for compacting on JSON files and reducing precicions of floating point values',
    'long_description': None,
    'author': 'Manu Chatterjee',
    'author_email': 'deftio@deftio.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/deftio/jsonvice',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
