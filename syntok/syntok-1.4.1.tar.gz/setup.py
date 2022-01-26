# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['syntok']

package_data = \
{'': ['*']}

install_requires = \
['regex>2016']

setup_kwargs = {
    'name': 'syntok',
    'version': '1.4.1',
    'description': 'Text tokenization and sentence segmentation (segtok v2).',
    'long_description': None,
    'author': 'Florian Leitner',
    'author_email': 'me@fnl.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
