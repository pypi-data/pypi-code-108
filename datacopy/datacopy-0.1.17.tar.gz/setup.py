# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dcp',
 'dcp.cli',
 'dcp.data_copy',
 'dcp.data_copy.copiers',
 'dcp.data_copy.copiers.to_database',
 'dcp.data_copy.copiers.to_file',
 'dcp.data_copy.copiers.to_memory',
 'dcp.data_format',
 'dcp.data_format.formats',
 'dcp.data_format.formats.database',
 'dcp.data_format.formats.file_system',
 'dcp.data_format.formats.memory',
 'dcp.storage',
 'dcp.storage.database',
 'dcp.storage.database.engines',
 'dcp.storage.file_system',
 'dcp.storage.file_system.engines',
 'dcp.storage.memory',
 'dcp.storage.memory.engines',
 'dcp.utils']

package_data = \
{'': ['*'], 'dcp.storage.database': ['sql_templates/*']}

install_requires = \
['PyYAML>=5.4.1',
 'SQLAlchemy>=1.4.7,<2.0.0',
 'cleo>=0.8.1,<0.9.0',
 'common-model>=0.2.0,<0.3.0',
 'loguru>=0.5.3,<0.6.0',
 'networkx>=2.5,<3.0',
 'pandas>=1.2.3,<2.0.0',
 'python-dateutil>=2.8.1,<3.0.0']

entry_points = \
{'console_scripts': ['dcp = dcp.cli:app']}

setup_kwargs = {
    'name': 'datacopy',
    'version': '0.1.17',
    'description': 'dcp - Data Copy',
    'long_description': None,
    'author': 'Ken Van Haren',
    'author_email': 'kenvanharen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.4',
}


setup(**setup_kwargs)
