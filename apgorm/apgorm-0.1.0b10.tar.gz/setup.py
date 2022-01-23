# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apgorm',
 'apgorm.constraints',
 'apgorm.migrations',
 'apgorm.sql',
 'apgorm.sql.generators',
 'apgorm.types',
 'apgorm.utils']

package_data = \
{'': ['*']}

install_requires = \
['asyncpg>=0.25.0,<0.26.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'apgorm',
    'version': '0.1.0b10',
    'description': 'A fully type-checked asynchronous ORM wrapped around asyncpg.',
    'long_description': '# apgorm\n[![pytest](https://github.com/TrigonDev/apgorm/actions/workflows/pytest.yml/badge.svg)](https://github.com/TrigonDev/apgorm/actions/workflows/pytest.yml)\n[![pypi](https://github.com/TrigonDev/apgorm/actions/workflows/pypi.yml/badge.svg)](https://pypi.org/project/apgorm)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/TrigonDev/apgorm/main.svg)](https://results.pre-commit.ci/latest/github/TrigonDev/apgorm/main)\n[![codecov](https://codecov.io/gh/TrigonDev/apgorm/branch/main/graph/badge.svg?token=LEY276K4NS)](https://codecov.io/gh/TrigonDev/apgorm)\n\n[Documentation](https://github.com/trigondev/apgorm/wiki) | [CONTRIBUTING.md](https://github.com/trigondev/.github/tree/main/CONTRIBUTING.md)\n\nAn asynchronous ORM wrapped around asyncpg. Examples can be found under `examples/`. Run examples with `python -m examples.<example_name>` (`python -m examples.basic`).\n\nPlease note that this library is not for those learning SQL or Postgres. Although the basic usage of apgorm is straightforward, you will run into problems, especially with migrations, if you don\'t understand regular SQL well.\n\nIf you need support, you can contact me `Circuit#3397` after joining [this server](https://discord.gg/dGAzZDaTS9). I don\'t accept friend requests.\n\n## Features\n - Fairly straightforward and easy-to-use.\n - Support for basic migrations.\n - Protects against SQL-injection.\n - Python-side converters and validators.\n - Decent many-to-many support.\n - Fully type-checked.\n - Tested.\n\n## Limitations\n - Limited column namespace. For example, you cannot have a column named `tablename` since that is used to store the name of the model.\n - Only supports PostgreSQL with asyncpg.\n - Migrations don\'t natively support field/table renaming, but you can still write your own migration with raw SQL.\n\n## Basic Usage\nDefining a model and database:\n```py\nclass User(apgorm.Model):\n    username = VarChar(32).field()\n    email = VarChar().nullablefield()\n    \n    primary_key = (username,)\n    \nclass Database(apgorm.Database):\n    users = User\n```\n\nIntializing the database:\n```py\ndb = Database(migrations_folder="path/to/migrations")\nawait db.connect(database="database name")\n```\n\nCreating & Applying migrations:\n```py\nif db.must_create_migrations():\n    db.create_migrations()\nif await db.must_apply_migrations():\n    await db.apply_migrations()\n```\n\nBasic create, fetch, update, and delete:\n```py\nuser = await User(username="Circuit").create()\nprint("Created user", user)\n\nassert user == await User.fetch(username="Circuit")\n\nuser.email.v = "email@example.com"\nawait user.save()\n\nawait user.delete()\n```\n',
    'author': 'Circuit',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TrigonDev/apgorm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
