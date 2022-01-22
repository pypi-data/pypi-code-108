# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['doorstop',
 'doorstop.cli',
 'doorstop.cli.tests',
 'doorstop.core',
 'doorstop.core.tests',
 'doorstop.core.validators',
 'doorstop.core.vcs',
 'doorstop.core.vcs.tests',
 'doorstop.gui',
 'doorstop.gui.tests',
 'doorstop.server',
 'doorstop.server.tests']

package_data = \
{'': ['*'],
 'doorstop': ['views/*'],
 'doorstop.cli.tests': ['docs/*', 'files/*'],
 'doorstop.core': ['files/*', 'files/assets/doorstop/*'],
 'doorstop.core.tests': ['docs/*',
                         'files/*',
                         'files/.venv/doorstop/reqs/*',
                         'files/a/*',
                         'files/a/b/*',
                         'files/child/*',
                         'files/external/*',
                         'files/new/*',
                         'files/parent/*',
                         'files/subfolder/*',
                         'test_fixtures/001-item-references-utf8-keyword/*',
                         'test_fixtures/001-item-references-utf8-keyword/files/*']}

install_requires = \
['Markdown>=3.3.3,<4.0.0',
 'PyYAML>=5.1,<6.0',
 'bottle>=0.12.13,<0.13.0',
 'openpyxl>=2.6,<3.0',
 'plantuml-markdown>=3.4.2,<4.0.0',
 'python-markdown-math>=0.6,<0.7',
 'requests>=2.0,<3.0']

entry_points = \
{'console_scripts': ['doorstop = doorstop.cli.main:main',
                     'doorstop-gui = doorstop.gui.main:main',
                     'doorstop-server = doorstop.server.main:main']}

setup_kwargs = {
    'name': 'doorstop',
    'version': '2.2',
    'description': 'Requirements management using version control.',
    'long_description': '[![Unix Build Status](https://img.shields.io/travis/com/doorstop-dev/doorstop/develop.svg?label=unix)](https://travis-ci.com/doorstop-dev/doorstop)\n[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/doorstop/develop.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/doorstop)\n<br>\n[![Coverage Status](http://img.shields.io/coveralls/doorstop-dev/doorstop/develop.svg)](https://coveralls.io/r/doorstop-dev/doorstop)\n[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/doorstop-dev/doorstop.svg)](https://scrutinizer-ci.com/g/doorstop-dev/doorstop/?branch=develop)\n[![PyPI Version](http://img.shields.io/pypi/v/Doorstop.svg)](https://pypi.org/project/Doorstop)\n<br>\n[![Gitter](https://badges.gitter.im/doorstop-dev/community.svg)](https://gitter.im/doorstop-dev/community)\n[![Google](https://img.shields.io/badge/forum-on_google-387eef)](https://groups.google.com/forum/#!forum/doorstop-dev)\n[![Best Practices](https://bestpractices.coreinfrastructure.org/projects/754/badge)](https://bestpractices.coreinfrastructure.org/projects/754)\n\n# Overview\n\nDoorstop is a [requirements management](http://alternativeto.net/software/doorstop/) tool that facilitates the storage of textual requirements alongside source code in version control.\n\n<img align="left" width="100" src="https://raw.githubusercontent.com/doorstop-dev/doorstop/develop/docs/images/logo-black-white.png"/>\n\nWhen a project leverages this tool, each linkable item (requirement, test case, etc.) is stored as a YAML file in a designated directory. The items in each directory form a document. The relationship between documents forms a tree hierarchy. Doorstop provides mechanisms for modifying this tree, validating item traceability, and publishing documents in several formats.\n\nDoorstop is under active development and we welcome contributions.\nThe project is licensed as [LGPLv3](https://github.com/doorstop-dev/doorstop/blob/develop/LICENSE.md).\nTo report a problem or a security vulnerability please [raise an issue](https://github.com/doorstop-dev/doorstop/issues).\nAdditional references:\n\n- publication: [JSEA Paper](http://www.scirp.org/journal/PaperInformation.aspx?PaperID=44268#.UzYtfWRdXEZ)\n- talks: [GRDevDay](https://speakerdeck.com/jacebrowning/doorstop-requirements-management-using-python-and-version-control), [BarCamp](https://speakerdeck.com/jacebrowning/strip-searched-a-rough-introduction-to-requirements-management)\n- sample: [Generated HTML](http://doorstop-dev.github.io/doorstop/)\n\n\n# Setup\n\n## Requirements\n\n* Python 3.5+\n* A version control system for requirements storage\n\n## Installation\n\nInstall Doorstop with pip:\n\n```sh\n$ pip install doorstop\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```sh\n$ poetry add doorstop\n```\n\nAfter installation, Doorstop is available on the command-line:\n\n```sh\n$ doorstop --help\n```\n\nAnd the package is available under the name \'doorstop\':\n\n```sh\n$ python\n>>> import doorstop\n>>> doorstop.__version__\n```\n\n# Usage\n\nSwitch to an existing version control working directory, or create one:\n\n```sh\n$ git init .\n```\n\n## Create documents\n\nCreate a new parent requirements document:\n\n```sh\n$ doorstop create SRD ./reqs/srd\n```\n\nAdd a few items to that document:\n\n```sh\n$ doorstop add SRD\n$ doorstop add SRD\n$ doorstop add SRD\n```\n\n## Link items\n\nCreate a child document to link to the parent:\n\n```sh\n$ doorstop create HLTC ./tests/hl --parent SRD\n$ doorstop add HLTC\n```\n\nLink items between documents:\n\n```sh\n$ doorstop link HLTC001 SRD002\n```\n\n## Publish reports\n\nRun integrity checks on the document tree:\n\n```sh\n$ doorstop\n```\n\nPublish the documents as HTML:\n\n```sh\n$ doorstop publish all ./public\n```\n',
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/Doorstop',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
