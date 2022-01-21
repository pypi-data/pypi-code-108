# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['roche_aws']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'roche-aws',
    'version': '0.0.0',
    'description': 'Empty roche_aws for security reasons',
    'long_description': None,
    'author': 'Iwan Silvan Bolzern',
    'author_email': 'iwan.bolzern@roche.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
