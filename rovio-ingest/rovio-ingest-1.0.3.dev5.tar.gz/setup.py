# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rovio_ingest', 'rovio_ingest.extensions']

package_data = \
{'': ['*']}

install_requires = \
['pyspark>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'rovio-ingest',
    'version': '1.0.3.dev5',
    'description': '',
    'long_description': None,
    'author': 'Vivek Balakrishnan',
    'author_email': 'vivek.balakrishnan@rovio.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
