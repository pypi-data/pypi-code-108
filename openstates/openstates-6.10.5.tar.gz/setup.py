# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openstates',
 'openstates.cli',
 'openstates.cli.tests',
 'openstates.data',
 'openstates.data.admin',
 'openstates.data.migrations',
 'openstates.data.models',
 'openstates.data.tests',
 'openstates.fulltext',
 'openstates.importers',
 'openstates.importers.tests',
 'openstates.metadata',
 'openstates.metadata._creation',
 'openstates.metadata.data',
 'openstates.metadata.tests',
 'openstates.models',
 'openstates.models.tests',
 'openstates.scrape',
 'openstates.scrape.schemas',
 'openstates.scrape.tests',
 'openstates.utils',
 'openstates.utils.people',
 'openstates.utils.tests']

package_data = \
{'': ['*'],
 'openstates.fulltext': ['raw/*'],
 'openstates.utils.tests': ['testdata/broken-committees/*',
                            'testdata/committees/*',
                            'testdata/data/*',
                            'testdata/people/data/pa/legislature/*',
                            'testdata/scraped-committees/*']}

install_requires = \
['Django>=3.2.0,<4.0.0',
 'PyYAML>=5.3.1,<6.0.0',
 'attrs>=20.2.0,<21.0.0',
 'boto3>=1.17.79,<2.0.0',
 'chardet>=3.0,<4.0',
 'click>=7.1.1,<8.0.0',
 'dj_database_url>=0.5.0,<0.6.0',
 'jsonschema>=3.2.0,<4.0.0',
 'psycopg2-binary>=2.8.4,<3.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pytz>=2019.3,<2020.0',
 'scrapelib>=2.0.2,<3.0.0',
 'spatula>=0.8.9,<0.9.0',
 'textract>=1.6,<2.0',
 'us>=2.0.2,<3.0.0']

entry_points = \
{'console_scripts': ['os-committees = openstates.cli.committees:main',
                     'os-initdb = openstates.cli.initdb:main',
                     'os-people = openstates.cli.people:main',
                     'os-scrape = openstates.cli.scrape:main',
                     'os-text-extract = openstates.cli.text_extract:main',
                     'os-update = openstates.cli.update:main',
                     'os-update-computed = openstates.cli.update_computed:main',
                     'os-us-to-yaml = openstates.cli.convert_us:main']}

setup_kwargs = {
    'name': 'openstates',
    'version': '6.10.5',
    'description': 'core infrastructure for the openstates project',
    'long_description': None,
    'author': 'James Turk',
    'author_email': 'james@openstates.org',
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
