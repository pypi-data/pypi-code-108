# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['los_docusign', 'los_docusign.migrations', 'los_docusign.utils']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.1.13,<4.0.0',
 'PyJWT==1.7.1',
 'django-environ>=0.4.5,<0.5.0',
 'django-lc-utils>=0.2.0,<0.3.0',
 'django-model-utils>=4.1.1,<5.0.0',
 'django-utils-six>=2.0,<3.0',
 'docusign-esign>=3.6.0,<4.0.0',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'los-docusign',
    'version': '0.3.3',
    'description': 'Docusign Django Wrapper for integrating DocuSign with Django Application',
    'long_description': None,
    'author': 'tejasb',
    'author_email': 'tejas@thesummitgrp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
