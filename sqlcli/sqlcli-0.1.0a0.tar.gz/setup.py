# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlcli', 'sqlcli._demo']

package_data = \
{'': ['*']}

install_requires = \
['rich>=11.0.0,<12.0.0', 'sqlmodel>=0.0.6,<0.0.7', 'typer>=0.3.0,<0.4.0']

entry_points = \
{'console_scripts': ['sqlcli = sqlcli.main:app']}

setup_kwargs = {
    'name': 'sqlcli',
    'version': '0.1.0a0',
    'description': 'A command line interface (CLI) for interacting with SQLModel.',
    'long_description': '# sqlcli\n\nA command line interface (CLI) for interacting with SQLModel.\n\n<hr>\n\n**Source code:** [https://github.com/SamEdwardes/sqlcli](https://github.com/SamEdwardes/sqlcli)\n\n**Docs:** [https://samedwardes.github.io/sqlcli/](https://samedwardes.github.io/sqlcli/)\n\n**PyPi:** *not yet published*\n\n<hr>\n\n## Installation\n\nYou can install *sqlcli* using pip:\n\n```bash\npip install sqlcli\n```\n\nThis will make the `sqlcli` command available in your python environment.\n\n## Usage\n\nThe quickest way to get started with *sqlcli* is to create a demo sqlite database:\n\n```bash\nsqlcli init-demo\n```\n\nThis will create a small sqlite database on your computer. The you can use sqlcli to explore your database.\n\n```bash\nsqlcli select athlete --database-url "sqlite:///demo_database.db" --models-module "demo_models.py"\n```\n',
    'author': 'SamEdwardes',
    'author_email': 'edwardes.s@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
