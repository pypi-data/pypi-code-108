# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eztea', 'eztea.sql', 'eztea.sql.migration', 'eztea.web']

package_data = \
{'': ['*'], 'eztea.sql.migration': ['template/*']}

install_requires = \
['ciso8601>=2.2.0',
 'falcon>=3.0.1',
 'python-dotenv>=0.12.0',
 'sqlalchemy-jsonfield>=1.0.0',
 'sqlalchemy-utc>=0.14.0',
 'sqlalchemy-utils>=0.38.2',
 'sqlalchemy>=1.3.19',
 'validr>=1.2.1']

extras_require = \
{'migration': ['alembic>=1.7.5',
               'black>=21.12b0',
               'click>=7.1.2',
               'mako>=1.1.6',
               'python-dateutil>=2.8.2'],
 'mysql': ['pymysql>=1.0.2'],
 'postgresql': ['psycopg2>=2.9.3']}

entry_points = \
{'console_scripts': ['eztea = eztea.__main__:main']}

setup_kwargs = {
    'name': 'eztea',
    'version': '0.1.0',
    'description': 'EZTea Web Framework',
    'long_description': '# EZTea Web Framework\n\n```\npip install eztea\n```\n\n## Usage\n\n```python\nfrom validr import T\n\nfrom eztea.web import Application, ResponderContext, Router\n\nrouter = Router()\n\n\n@router.get("/")\ndef hello(\n    ctx: ResponderContext,\n    name: str = T.str.default("world"),\n) -> T.dict(hello=T.str):\n    return {"hello": name}\n\n\napp = Application()\napp.include_router(router)\n```\n',
    'author': 'guyskk',
    'author_email': 'guyskk@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/guyskk/eztea',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.4,<4.0',
}


setup(**setup_kwargs)
