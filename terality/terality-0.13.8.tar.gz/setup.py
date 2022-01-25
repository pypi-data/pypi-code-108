# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['common_client_scheduler',
 'common_client_scheduler.protobuf.generated',
 'terality',
 'terality._terality',
 'terality._terality._testing',
 'terality._terality.bin',
 'terality._terality.data_transfers',
 'terality._terality.encoding',
 'terality._terality.terality_structures',
 'terality._terality.utils',
 'terality_serde']

package_data = \
{'': ['*'], 'common_client_scheduler': ['protobuf/*']}

install_requires = \
['aiobotocore>=2.0,<3.0',
 'boto3>=1.19.8,<1.19.9',
 'click>=8.0.1,<9.0.0',
 'cloudpickle>=2.0.0,<3.0.0',
 'numpy>=1.18,<2.0',
 'pandas>=1.0.0,<2.0.0',
 'protobuf>=3.9.1,<4.0.0',
 'pyarrow>=6.0.0,<7.0.0',
 'pydantic>=1.7.3,<2.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'requests>=2.26.0,<3.0.0',
 'sentry-sdk>=1.3.0,<2.0.0',
 'single-source>=0.1.5,<0.2.0',
 'typing_extensions>=3.10.0,<4.0.0',
 'urllib3>=1.26.0']

extras_require = \
{'azure': ['azure-storage-file-datalake>=12.4.0,<13.0.0',
           'azure-storage-blob>=12.8.1,<13.0.0',
           'azure-identity>=1.6.0,<2.0.0']}

entry_points = \
{'console_scripts': ['terality = terality._terality.bin.__main__:cli']}

setup_kwargs = {
    'name': 'terality',
    'version': '0.13.8',
    'description': 'The Data Processing Engine for Data Scientists',
    'long_description': 'Terality is the serverless & lightning fast Python data processing engine.\n\nTerality’s engine enable data scientists and engineers to transform and manipulate data at light speed, with the exact same syntax as Pandas, with zero sever management.\n\nYou will need a Terality account to use this package. Check out our documentation to get started https://docs.terality.com/.',
    'author': 'Terality Engineering Team',
    'author_email': 'dev.null@terality.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://terality.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
