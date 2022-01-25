# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_storage', 'views_storage.backends', 'views_storage.serializers']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.29,<2.0.0',
 'azure-storage-blob>=12.9.0,<13.0.0',
 'cryptography>=36.0.1,<37.0.0',
 'environs>=9.3.5,<10.0.0',
 'lz4>=3.1.10,<4.0.0',
 'pandas>=1.3.5,<2.0.0',
 'paramiko>=2.9.1,<3.0.0',
 'psycopg2>=2.9.3,<3.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'views-storage',
    'version': '0.6.0',
    'description': 'Storage driver used throughout views 3.',
    'long_description': None,
    'author': 'Mihai Croicu',
    'author_email': 'mihai.croicu@pcr.uu.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/uppsalaconflictdataprogram/views_storage',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
