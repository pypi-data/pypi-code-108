# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['p3orm']

package_data = \
{'': ['*']}

install_requires = \
['PyPika>=0.48.8,<0.49.0', 'asyncpg>=0.24.0,<0.25.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'p3orm',
    'version': '0.1.0',
    'description': 'Python PyPika Postgres ORM',
    'long_description': "# porm\n\nMinimal PostgreSQL Python ORM, backed by [asyncpg](https://github.com/MagicStack/asyncpg), [Pydantic](https://github.com/samuelcolvin/pydantic), and [PyPika](https://github.com/kayak/pypika). \n\n## Philosophy\n\n90% of the time we talk to a database is with a CRUD operation. porm provides helpers\n\nThe remaining 10% is a bit more complicated. porm doesn't attempt to hide SQL queries behind any magic, instead it empowers you to write direct, explicit, and legible SQL queries with [PyPika](https://github.com/kayak/pypika).\n\nObject created or fetched by porm are **dead**, they're just (currently) Pydantic models. If you want to manipulate the database, you do so explicitly.\n\n\n## Roadmap\n\n- [ ] Annotation type definition\n- [ ] Relationships\n- [ ] Tests\n- [ ] Look into [attrs](https://github.com/python-attrs/attrs) over pydantic (does this actually need type *validation*)\n",
    'author': 'Rafal Stapinski',
    'author_email': 'stapinskirafal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rafalstapinski/porm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
