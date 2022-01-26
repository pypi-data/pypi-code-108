# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbt_client']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

setup_kwargs = {
    'name': 'dbt-client',
    'version': '0.1.2',
    'description': 'A simple client for DBT RPC instances',
    'long_description': '# dbt-client\nA simple client for DBT RPC instances\n',
    'author': 'Gabriel Gazola Milan',
    'author_email': 'gabriel.gazola@poli.ufrj.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gabriel-milan/dbt-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
