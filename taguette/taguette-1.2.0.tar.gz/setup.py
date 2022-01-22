# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taguette',
 'taguette.migrations',
 'taguette.migrations.versions',
 'taguette.web']

package_data = \
{'': ['*'],
 'taguette': ['l10n/de_DE/LC_MESSAGES/*',
              'l10n/es_ES/LC_MESSAGES/*',
              'l10n/fr_FR/LC_MESSAGES/*',
              'l10n/it_IT/LC_MESSAGES/*',
              'l10n/nl_NL/LC_MESSAGES/*',
              'l10n/pt_BR/LC_MESSAGES/*',
              'static/*',
              'static/css/*',
              'static/js/*',
              'static/webfonts/*',
              'templates/*']}

install_requires = \
['SQLAlchemy>=1.4,<1.5',
 'XlsxWriter>=1.4,<1.5',
 'alembic>=1.6,<1.8',
 'beautifulsoup4',
 'bleach>=3,<4',
 'html5lib>=1,<2',
 'jinja2>=3,<3.1',
 'opentelemetry-api>=1.5,<1.7',
 'prometheus-async',
 'prometheus-client',
 'redis>=3,<4',
 'sentry-sdk',
 'tornado>=6.1']

extras_require = \
{'otel': ['opentelemetry-instrumentation-sqlalchemy>=0.24b0,<0.26',
          'opentelemetry-instrumentation-tornado>=0.24b0,<0.26']}

entry_points = \
{'console_scripts': ['taguette = taguette.main:main']}

setup_kwargs = {
    'name': 'taguette',
    'version': '1.2.0',
    'description': 'Document tagger for qualitative analysis',
    'long_description': 'Taguette\n========\n\nA spin on the phrase "tag it!", `Taguette <https://www.taguette.org/>`__ is a free and open source qualitative research tool that allows users to:\n\n+ Import PDFs, Word Docs (``.docx``), Text files (``.txt``), HTML, EPUB, MOBI, Open Documents (``.odt``), and Rich Text Files (``.rtf``).\n+ Highlight words, sentences, or paragraphs and tag them with the codes *you* create.\n+ (not yet) Group imported documents together (e.g. as \'Interview\' or \'Lit Review\').\n+ Export tagged documents, highlights for a specific tag, a list of tags with description and colors, and whole projects.\n\n`Check out our website to learn more about how to install and get started. <https://www.taguette.org/>`__\n\nMotivation and goal\n-------------------\n\nQualitative methods generate rich, detailed research materials that leave individuals’ perspectives intact  as well as provide multiple contexts for understanding phenomenon under study. Qualitative methods are used by a wide range of fields, such as anthropology, education, nursing, psychology, sociology, and marketing. Qualitative data has a similarly wide range: observations, interviews, documents, audiovisual materials, and more.\n\nHowever - the software options for qualitative researchers are either **far too expensive**, don\'t allow for the seminal method of highlighting and tagging materials, *or actually perform quantitative analysis*, just on text.\n\n**It\'s not right or fair that qualitative researchers without massive research funds cannot afford the basic software to do their research.**\n\nSo, to bolster a fair and equitable entry into qualitative methods, we\'ve made Taguette!\n\nInstallation\n------------\n\nYou can find complete installation instructions on `our website <https://www.taguette.org/install.html>`__, including installers for Windows and MacOS.\n\nDevelopment setup from the repository\n-------------------------------------\n\nYou can install from a local clone of this repository, which will allow you to easily change the sources to suit your needs:\n\n1. Clone this git repository from the terminal: ``git clone https://gitlab.com/remram44/taguette.git``\n2. Navigate on the command line to the repository you\'ve just cloned locally, using the ``cd`` command. To get help using ``cd``, use `this tutorial <https://swcarpentry.github.io/shell-novice/02-filedir/index.html>`__.\n3. Taguette uses `Poetry <https://python-poetry.org/>`__ for its packaging and dependency management. You will need to `install Poetry <https://python-poetry.org/docs/#installation>`__.\n4. Install Taguette and its dependencies by running ``poetry install``. Poetry will create a virtual environment for you by default, activate it by running ``poetry shell``.\n5. Build translation files using ``scripts/update_translations.sh``.\n6. You can start taguette in development mode using ``taguette --debug`` (or ``taguette --debug server <config_file>``). This will start Tornado in debug mode, which means in particular that it will auto-restart every time you make changes.\n7. Navigate to `localhost:7465 <http://localhost:7465/>`__ to use Taguette!\n\nLicense\n-------\n\n* Copyright (C) 2018, Rémi Rampin and Taguette contributors\n\nLicensed under a **BSD 3-clause "New" or "Revised" License**. See the `LICENSE <LICENSE.txt>`__ for details.\n',
    'author': 'Remi Rampin',
    'author_email': 'remi@rampin.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.taguette.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
