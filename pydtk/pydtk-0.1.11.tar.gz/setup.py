# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydtk',
 'pydtk.bin',
 'pydtk.bin.sub_commands',
 'pydtk.builder',
 'pydtk.builder.dbdb',
 'pydtk.db',
 'pydtk.db.v1',
 'pydtk.db.v1.handlers',
 'pydtk.db.v2',
 'pydtk.db.v2.handlers',
 'pydtk.db.v2.search_engines',
 'pydtk.db.v3',
 'pydtk.db.v3.handlers',
 'pydtk.db.v3.search_engines',
 'pydtk.db.v4',
 'pydtk.db.v4.deps',
 'pydtk.db.v4.deps.pql_python37',
 'pydtk.db.v4.deps.pql_python37.pql',
 'pydtk.db.v4.deps.pql_python38',
 'pydtk.db.v4.deps.pql_python38.pql',
 'pydtk.db.v4.engines',
 'pydtk.db.v4.handlers',
 'pydtk.io',
 'pydtk.models',
 'pydtk.models.autoware',
 'pydtk.models.pointcloud',
 'pydtk.models.zstd',
 'pydtk.preprocesses',
 'pydtk.statistics',
 'pydtk.utils']

package_data = \
{'': ['*'], 'pydtk': ['conf/*']}

install_requires = \
['attrdict',
 'bitstring>=3.1.7,<4.0.0',
 'deepmerge>=0.1.1,<0.2.0',
 'fire>=0.3.1,<0.4.0',
 'flatten-dict>=0.3.0,<0.4.0',
 'montydb[lmdb,bson]>=2.3.12,<3.0.0',
 'numpy>=1.16.6,<2.0.0',
 'opencv-python>=4.2.0.34,<5.0.0.0',
 'pandas>=1.0.3,<2.0.0',
 'pymongo>=3.11.3,<4.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'pyyaml',
 'six>=1.15.0,<2.0.0',
 'sqlalchemy-migrate',
 'sqlalchemy>=1.3.17,<2.0.0',
 'tinydb>=3.2.1,<4.0.0',
 'tinymongo>=0.2.0,<0.3.0',
 'tqdm>=4.46.1,<5.0.0']

extras_require = \
{'pointcloud': ['pyntcloud'],
 'ros': ['pycryptodomex', 'gnupg', 'rospkg', 'flatdict>=4.0.1,<5.0.0'],
 'zstd': ['pyzstd>=0.15.0,<0.16.0']}

entry_points = \
{'console_scripts': ['analyze_statistics = pydtk.builder.statistic_db:script',
                     'batch_analyze_statistics = '
                     'pydtk.builder.statistic_db:batch_script',
                     'create_meta_db = pydtk.builder.meta_db:script',
                     'make_meta = pydtk.bin.make_meta:main',
                     'pydtk = pydtk.bin.cli:script']}

setup_kwargs = {
    'name': 'pydtk',
    'version': '0.1.11',
    'description': 'A Python toolkit for managing, retrieving and processing data.',
    'long_description': '# Python Dataware Toolkit\n\nA Python toolkit for managing, retrieving, and processing data.\n\n## Installation\nYou can install the toolkit with:\n```bash\n$ pip3 install pydtk\n\n```\n\nIf you want to install the toolkit with extra feature (e.g. support for PointCloud and ROS), \nyou can install it with extra dependencies as follows:\n```bash\n$ pip3 install pydtk[pointcloud,ros]\n\n```\n\nSome PyDTK models require additional packages.  \nPlease refer the following table and install them manually with command `pip install ...`.  \n\n| PyDTK model | Required packages |\n| --- | --- |\n| rosbag.* | ros_numpy (https://github.com/eric-wieser/ros_numpy.git) |\n| pointcloud.PCDModel | pypcd (https://github.com/klintan/pypcd.git) |\n\n\n## Usage\n\nBy using Pydtk, you can load a variety of types of data with a unified interface as shown below.\n\n1. Load DBHandler for retrieving metadata\n```python\nfrom pydtk.db import DBHandler\n\n# Initialize handler (This will read all the metadata from DB on initialization)\nhandler = DBHandler(\n    db_class=\'meta\',\n    db_host=\'./examples/example_db\',\n    base_dir_path=\'./test\'\n)\n\n```\n\n2. Read metadata from db with data selection.\n```python\n# Select by timestamp\nhandler.read(pql=\'start_timestamp > 1420000000 and end_timestamp < 1500000000\')\nprint(handler.data)\n\n# Select by record-id\nhandler.read(pql=\'record_id == regex("test.*")\')\nprint(handler.data)\n\n```\n\n3. Load data from files based on metadata.\n```python\nfrom pydtk.io import BaseFileReader, NoModelMatchedError\n\nreader = BaseFileReader()\n\ntry:\n    for sample in handler:\n        print(\'loading content "{0}" from file "{1}"\'.format(sample[\'contents\'], sample[\'path\']))\n        try:\n            timestamps, data, columns = reader.read(sample)\n            assert print(data)\n        except NoModelMatchedError as e:\n            print(str(e))\n            continue\nexcept EOFError:\n    pass\n```\n\n\n## Documentation\nFor more information about this toolkit, please refer the [document](https://dataware-tools.github.io/pydtk/).\n\n\n## Setup for contribution\nTo improve this toolkit, firstly clone this repository and then \nrun the following command to prepare the environment. \n\n```bash\n$ git clone git@github.com:dataware-tools/pydtk.git --recurse-submodules\n$ poetry install\n\n```\n\nMake sure that [poetry](https://python-poetry.org/) is installed before executing the command.\n\nIf you want to install the toolkit with extra feature (e.g. support for ROS), \nplease specify it with `-E` option.  \nExample (installation with `pointcloud` and `ros` extras):\n```bash\n$ poetry install -E pointcloud -E ros\n\n```\n',
    'author': 'Yusuke Adachi',
    'author_email': 'adachi.yusuke@hdwlab.co.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dataware-tools/python-toolkit.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
