# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['frontegg',
 'frontegg.baseConfig',
 'frontegg.fastapi',
 'frontegg.fastapi.secure_access',
 'frontegg.flask',
 'frontegg.flask.secure_access',
 'frontegg.helpers',
 'frontegg.sanic',
 'frontegg.sanic.secure_access']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.1.1,<2.0.0',
 'cryptography>=36.0,<37.0',
 'pyjwt>=2.3,<3.0',
 'requests>=2.22.0,<3.0.0']

extras_require = \
{'fastapi': ['fastapi'], 'flask': ['flask>=1.0,<2.0']}

setup_kwargs = {
    'name': 'frontegg',
    'version': '1.0.17',
    'description': 'Frontegg is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.',
    'long_description': '.. image:: https://fronteggstuff.blob.core.windows.net/frongegg-logos/logo-transparent.png\n   :alt: Frontegg\n\nFrontegg is a web platform where SaaS companies can set up their fully managed, scalable and brand aware - SaaS features and integrate them into their SaaS portals in up to 5 lines of code.\n\nFor more information and usage you can visit the `github repo <https://github.com/frontegg/python-sdk>`_.',
    'author': 'Frontegg LTD',
    'author_email': 'hello@frontegg.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://frontegg.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
