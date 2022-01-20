# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datanommer', 'datanommer.models', 'datanommer.models.testing']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.0.9,<1.4.23',
 'alembic>=1.6.5,<2.0.0',
 'fedora-messaging>=2.1.0,<3.0.0',
 'psycopg2>=2.9.1,<3.0.0']

extras_require = \
{'schemas': ['anitya-schema',
             'fedora-messaging-the-new-hotness-schema',
             'bodhi-messages',
             'fedocal-messages',
             'fedora-planet-messages',
             'noggin-messages',
             'fedorainfra-ansible-messages',
             'nuancier-messages',
             'discourse2fedmsg-messages',
             'copr-messaging']}

setup_kwargs = {
    'name': 'datanommer.models',
    'version': '1.0.2',
    'description': 'SQLAlchemy models for datanommer',
    'long_description': 'datanommer.models\n=================\n\nThis package contains the SQLAlchemy data model for datanommer.\n\nDatanommer is a storage consumer for the Fedora Infrastructure Message Bus\n(fedmsg).  It is comprised of a `fedmsg <http://fedmsg.com>`_ consumer that\nstuffs every message into a sqlalchemy database.\n',
    'author': 'Fedora Infrastructure',
    'author_email': 'admin@fedoraproject.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fedora-infra/datanommer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
