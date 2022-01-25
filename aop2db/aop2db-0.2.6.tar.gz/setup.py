# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aop2db', 'aop2db.aop', 'aop2db.orm']

package_data = \
{'': ['*']}

install_requires = \
['Click>=8.0,<9.0',
 'cryptography>=35.0.0,<36.0.0',
 'lxml>=4.6.5,<5.0.0',
 'pandas>=1.3.1,<2.0.0',
 'pymysql>=1.0.2,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'sqlalchemy>=1.4.22,<2.0.0',
 'sqlalchemy_utils>=0.37.8,<0.38.0',
 'tqdm>=4.62.0,<5.0.0',
 'xmltodict==0.12.0']

setup_kwargs = {
    'name': 'aop2db',
    'version': '0.2.6',
    'description': 'AOP2DB - Python parser for converting importing adverse outcome pathway data into a relational database.',
    'long_description': None,
    'author': 'Bruce Schultz',
    'author_email': 'bruce.schultz@scai.fraunhofer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
