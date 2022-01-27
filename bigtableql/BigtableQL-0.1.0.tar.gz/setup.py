# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bigtableql']

package_data = \
{'': ['*']}

install_requires = \
['datafusion==0.4.0',
 'google-cloud-bigtable==2.4.0',
 'pyarrow==6.0.1',
 'sqloxide==0.1.13']

setup_kwargs = {
    'name': 'bigtableql',
    'version': '0.1.0',
    'description': 'Query Layer for Google Cloud Bigtable',
    'long_description': None,
    'author': 'jychen7',
    'author_email': 'jychen7@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
