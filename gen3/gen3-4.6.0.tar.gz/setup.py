# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gen3',
 'gen3.cli',
 'gen3.tools',
 'gen3.tools.bundle',
 'gen3.tools.download',
 'gen3.tools.indexing',
 'gen3.tools.metadata']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp',
 'backoff',
 'click',
 'dataclasses-json',
 'drsclient<1.0.0',
 'fastavro>=1.4.7,<2.0.0',
 'humanfriendly',
 'indexclient>=1.6.2',
 'jsonschema',
 'pandas',
 'pypfb<1.0.0',
 'python-dateutil',
 'requests',
 'tqdm>=4.61.2']

entry_points = \
{'console_scripts': ['gen3 = gen3.cli.__main__:main']}

setup_kwargs = {
    'name': 'gen3',
    'version': '4.6.0',
    'description': 'Gen3 CLI and Python SDK',
    'long_description': None,
    'author': 'Center for Translational Data Science at the University of Chicago',
    'author_email': 'support@datacommons.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gen3.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<=3.10',
}


setup(**setup_kwargs)
