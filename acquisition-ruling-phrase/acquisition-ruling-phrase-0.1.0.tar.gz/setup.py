# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['acquisition_ruling_phrase',
 'acquisition_ruling_phrase.dispositive',
 'acquisition_ruling_phrase.patterns',
 'acquisition_ruling_phrase.tags']

package_data = \
{'': ['*']}

install_requires = \
['acquisition-sanitizer>=0.2.0,<0.3.0',
 'beautifulsoup4>=4.10,<5.0',
 'html5lib>=1.1,<2.0']

setup_kwargs = {
    'name': 'acquisition-ruling-phrase',
    'version': '0.1.0',
    'description': 'Pattern matching common phrases in Supreme Court decisions indicating the start of content with doctrinal value.',
    'long_description': None,
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
