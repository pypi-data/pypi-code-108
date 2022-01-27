# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tft',
 'tft.artemis',
 'tft.artemis.api',
 'tft.artemis.drivers',
 'tft.artemis.scripts',
 'tft.artemis.tasks']

package_data = \
{'': ['*'], 'tft.artemis': ['schema/*', 'schema/drivers/*']}

install_requires = \
['Pint>=0.17,<0.18',
 'alembic>=1.7.4,<2.0.0',
 'awscli>=1.20.30,<2.0.0',
 'beaker-client>=28.2,<29.0',
 'click>=8.0.1,<9.0.0',
 'dramatiq[rabbitmq]>=1.7.0,<2.0.0',
 'gluetool>=1.24,<2.0',
 'gunicorn==20.1.0',
 'jinja2-ansible-filters>=1.3.0,<2.0.0',
 'jq>=1.1.3,<2.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'molten>=1.0.1,<2.0.0',
 'periodiq>=0.12.1,<0.13.0',
 'psycopg2>=2.9.1,<3.0.0',
 'pyinstrument>=4.0.2,<5.0.0',
 'python-openstackclient>=5.0.0,<6.0.0',
 'redis>=3.5.3,<4.0.0',
 'sqlalchemy-utils>=0.37.8,<0.38.0',
 'sqlalchemy>=1.4,<1.4.23',
 'stackprinter>=0.2.4,<0.3.0',
 'typing-extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['artemis-api-server = tft.artemis.api:main',
                     'artemis-db-init-content = '
                     'tft.artemis.scripts.init_db_content:cmd_root',
                     'artemis-dispatcher = tft.artemis.dispatcher:main',
                     'artemis-worker = tft.artemis.scripts.worker:cmd_root']}

setup_kwargs = {
    'name': 'tft-artemis',
    'version': '0.0.33',
    'description': 'Artemis is a machine provisioning service. Its goal is to provision a machine - using a set of preconfigured providers as backends - which would satisfy the given hardware and software requirements.',
    'long_description': None,
    'author': 'Milos Prchlik',
    'author_email': 'mprchlik@redhat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.8',
}


setup(**setup_kwargs)
