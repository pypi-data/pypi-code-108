# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['keycloak',
 'keycloak.core',
 'keycloak.core.asynchronous',
 'keycloak.extensions']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'cached-property>=1.5.2,<2.0.0',
 'httpx>=0.18.2,<0.19.0',
 'python-jose[cryptography]>=3.3.0,<4.0.0']

extras_require = \
{'docs': ['Sphinx>=4.0.2,<5.0.0', 'sphinx-rtd-theme>=0.5.2,<0.6.0'],
 'extensions': ['Flask>=2.0.1,<3.0.0',
                'starlette>=0.15.0,<0.16.0',
                'Django>=3.2.4,<4.0.0',
                'uvicorn>=0.14.0,<0.15.0']}

setup_kwargs = {
    'name': 'keycloak',
    'version': '3.1.3',
    'description': 'Python client for Keycloak IAM',
    'long_description': None,
    'author': 'Akhil Lawrence',
    'author_email': 'akhilputhiry@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
