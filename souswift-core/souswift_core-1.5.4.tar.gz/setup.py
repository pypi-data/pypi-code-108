# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['souswift_core',
 'souswift_core.exc',
 'souswift_core.filters',
 'souswift_core.providers',
 'souswift_core.providers.database']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.29,<2.0.0',
 'aiomysql>=0.0.22,<0.0.23',
 'context-handler>=2.1.0,<3.0.0',
 'fastapi>=0.71.0,<0.72.0',
 'pydantic[email]>=1.9.0,<2.0.0',
 'ujson>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'souswift-core',
    'version': '1.5.4',
    'description': '',
    'long_description': None,
    'author': 'Gustavo Correa',
    'author_email': 'self.gustavocorrea@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
