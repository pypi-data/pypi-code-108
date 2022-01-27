# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slai', 'slai.clients', 'slai.modules']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.11,<4.0.0',
 'Jinja2>=2.11.2,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'boto3>=1.16.44,<2.0.0',
 'celery==5.0.2',
 'click>=7.1.2,<8.0.0',
 'python-dotenv>=0.15.0,<0.16.0',
 'redis>=3.5.3,<4.0.0',
 'requests>=2.26.0,<3.0.0',
 'shtab>=1.3.4,<2.0.0',
 'tqdm>=4.61.1,<5.0.0',
 'urllib3>=1.26.7,<2.0.0',
 'xxhash>=2.0.2,<3.0.0']

setup_kwargs = {
    'name': 'slai',
    'version': '0.1.59',
    'description': '',
    'long_description': None,
    'author': 'slai',
    'author_email': 'luke@slai.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
