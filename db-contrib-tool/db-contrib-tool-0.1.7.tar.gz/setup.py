# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['db_contrib_tool',
 'db_contrib_tool.bisect',
 'db_contrib_tool.setup_repro_env',
 'db_contrib_tool.symbolizer',
 'db_contrib_tool.utils']

package_data = \
{'': ['*'], 'db_contrib_tool': ['config/*']}

install_requires = \
['PyGithub==1.55',
 'PyYAML==6.0',
 'analytics-python==1.4.0',
 'distro==1.6.0',
 'evergreen.py==3.4.2',
 'oauthlib==3.1.1',
 'packaging>=21.3,<22.0',
 'pkce==1.0.3',
 'pydantic==1.8.2',
 'requests-oauthlib==1.3.0',
 'requests==2.26.0',
 'structlog==21.4.0']

entry_points = \
{'console_scripts': ['db-contrib-tool = db_contrib_tool.cli:main']}

setup_kwargs = {
    'name': 'db-contrib-tool',
    'version': '0.1.7',
    'description': "The `db-contrib-tool` - MongoDB's tool for contributors.",
    'long_description': None,
    'author': 'STM team',
    'author_email': 'dev-prod-stm@10gen.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
