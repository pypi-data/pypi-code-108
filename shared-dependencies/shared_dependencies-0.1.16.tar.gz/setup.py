# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['shared_dependencies']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.3.0,<3.0.0',
 'asttokens>=2.0.5,<3.0.0',
 'colorama>=0.4.4,<0.5.0',
 'cryptography>=36.0.1,<37.0.0',
 'executing>=0.8.2,<0.9.0',
 'httpx>=0.21.1,<0.22.0',
 'pure-eval>=0.2.1,<0.3.0',
 'pycrypto>=2.6.1,<3.0.0',
 'pydantic[dotenv]>=1.9.0,<2.0.0',
 'sentry-sdk>=1.5.1,<2.0.0',
 'tenacity>=8.0.1,<9.0.0']

setup_kwargs = {
    'name': 'shared-dependencies',
    'version': '0.1.16',
    'description': '',
    'long_description': None,
    'author': 'Jean-Charles Bouchaud',
    'author_email': 'jeancharles-b@evidenceb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
