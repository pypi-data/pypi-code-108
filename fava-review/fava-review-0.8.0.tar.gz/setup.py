# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fava_review', 'fava_review.templates']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0', 'fava>=1.20.1,<2.0.0', 'petl>=1.7.4,<2.0.0']

setup_kwargs = {
    'name': 'fava-review',
    'version': '0.8.0',
    'description': 'A Fava extension to help review transactions over a series of periods.',
    'long_description': None,
    'author': 'Jakub Jamro',
    'author_email': 'kuba.jamro@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
