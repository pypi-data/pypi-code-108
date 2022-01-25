# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

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
    'version': '0.2.9',
    'description': 'AOP2DB - Python parser for converting importing adverse outcome pathway data into a relational database.',
    'long_description': '====================================================\nAOP2DB |docs| |python_versions| |travis| |coverage|\n====================================================\n\nPackage for compiling the adverse outcome pathway (AOP) data into a relational database. The data is publicly available at the `AOP website <https://aopwiki.org/>`_.\n\nInstallation |pypi_version| |pypi_license|\n==========================================\n\n``aop2db`` can be directly installed from PyPi with pip::\n\n    $ pip install aop2db\n\nUsage\n=====\n\nTo load the data into a relational database::\n\n    $ aop2db load\n\nTo set the driver of your database::\n\n    $ aop2db conn mysql+pymysql://<user>:<password>@<server>/<database>\n\nDisclaimer\n==========\nAOP2DB is a scientific software that has been developed in an academic capacity, and thus comes with no warranty or\nguarantee of maintenance, support, or back-up of data.\n\n\n.. |pypi_version| image:: https://img.shields.io/pypi/v/aop2db.svg\n    :target: https://pypi.python.org/pypi/aop2db\n    :alt: Current version on PyPI\n\n.. |python_versions| image:: https://img.shields.io/pypi/pyversions/aop2db.svg\n    :alt: Stable Supported Python Versions\n\n.. |travis| image:: https://app.travis-ci.com/brucetony/aop2db.svg?branch=master\n    :alt: Current build status\n\n.. |docs| image:: https://readthedocs.org/projects/aop2db/badge/?version=latest\n        :target: https://readthedocs.org/projects/aop2db/badge/?version=latest\n        :alt: Documentation Status\n\n.. |pypi_license| image:: https://img.shields.io/pypi/l/aop2db.svg\n    :alt: MIT\n\n.. |coverage| image:: https://codecov.io/gh/brucetony/aop2db/branch/master/graphs/badge.svg?\n    :alt: Coverage Status',
    'author': 'Bruce Schultz',
    'author_email': 'bruce.schultz@scai.fraunhofer.de',
    'maintainer': 'Bruce Schultz',
    'maintainer_email': 'bruce.schultz@scai.fraunhofer.de',
    'url': 'https://github.com/brucetony/aop2db',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
