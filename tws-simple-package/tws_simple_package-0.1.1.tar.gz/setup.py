# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tws_simple_package']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=4.4.0,<5.0.0']

entry_points = \
{'console_scripts': ['tws_simple_package = '
                     'tws_simple_package.tws_simple_package:main']}

setup_kwargs = {
    'name': 'tws-simple-package',
    'version': '0.1.1',
    'description': 'Simple Poetry Package',
    'long_description': None,
    'author': 'Taylor Santiago',
    'author_email': 'tsanti928@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
