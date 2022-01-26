# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rypython',
 'rypython.randas',
 'rypython.rex',
 'rypython.rexcel',
 'rypython.ry365',
 'rypython.rytime',
 'rypython.scripts']

package_data = \
{'': ['*']}

install_requires = \
['O365>=2.0.14,<3.0.0', 'XlsxWriter>=3.0.2,<4.0.0', 'pandas>=1.2.1,<2.0.0']

setup_kwargs = {
    'name': 'rypython',
    'version': '1.2.1',
    'description': '',
    'long_description': None,
    'author': "Ryan O'Rourke",
    'author_email': 'raorourke@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
