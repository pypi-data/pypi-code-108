# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bookserver', 'bookserver.internal', 'bookserver.routers']

package_data = \
{'': ['*'], 'bookserver': ['templates/auth/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'SQLAlchemy>=1.4.11,<2.0.0',
 'aiofiles>=0.6.0,<0.7.0',
 'aioredis>=2.0.0,<3.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'alembic>=1.4.3,<2.0.0',
 'async-timeout>=3.0.0,<4.0.0',
 'asyncpg>=0.22.0,<0.23.0',
 'bleach>=3.3.0,<4.0.0',
 'celery[redis]>=5.1.2,<6.0.0',
 'fastapi-login==1.6.3',
 'fastapi>=0.68.0,<0.69.0',
 'multi-await>=1.0.1,<2.0.0',
 'pydal>=20210215.1,<20210216.0',
 'pyhumps>=3.0.2,<4.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'redis>=3.5.3,<4.0.0',
 'runestone>=6.0.0,<7.0.0',
 'uvicorn[standard]>=0.14.0,<0.15.0']

extras_require = \
{':sys_platform != "win32"': ['gunicorn>=20.1.0,<21.0.0']}

entry_points = \
{'console_scripts': ['bookserver = bookserver.__main__:run']}

setup_kwargs = {
    'name': 'bookserver',
    'version': '1.1.6',
    'description': 'A new Runestone Server Framework',
    'long_description': '*******************************************\nNew FastAPI-based Book Server for Runestone\n*******************************************\nThe BookServer is a next-generation server for the `Runestone platform <https://runestone.academy/>`_. The goal of this project is to replace the parts of the web2py-based RunestoneServer. For more information, see the `full documentation <https://bookserver.readthedocs.io/en/latest/>`_.\n\nWe would love development help on this; see the `developer docs <https://bookserver.readthedocs.io/en/latest/docs/dev_toctree.html>`_.\n\nTODO: A nice image of a book or something eye-catching.',
    'author': 'Brad Miller',
    'author_email': 'bonelake@mac.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
