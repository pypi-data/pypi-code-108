# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['li_api', 'li_api.li_topics', 'li_api.li_topics.pii_analysis_requests']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-tools==1.29.0', 'grpcio==1.29.0', 'protobuf==3.12.2']

setup_kwargs = {
    'name': 'li-api',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'lex',
    'author_email': 'lex@legatoivy.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
