# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ramstk',
 'ramstk.analyses',
 'ramstk.analyses.milhdbk217f',
 'ramstk.analyses.milhdbk217f.models',
 'ramstk.analyses.statistics',
 'ramstk.db',
 'ramstk.exim',
 'ramstk.models',
 'ramstk.models.commondb',
 'ramstk.models.commondb.site_info',
 'ramstk.models.programdb',
 'ramstk.models.programdb.action',
 'ramstk.models.programdb.allocation',
 'ramstk.models.programdb.cause',
 'ramstk.models.programdb.control',
 'ramstk.models.programdb.design_electric',
 'ramstk.models.programdb.design_mechanic',
 'ramstk.models.programdb.environment',
 'ramstk.models.programdb.failure_definition',
 'ramstk.models.programdb.fmea',
 'ramstk.models.programdb.function',
 'ramstk.models.programdb.hardware',
 'ramstk.models.programdb.hazard',
 'ramstk.models.programdb.mechanism',
 'ramstk.models.programdb.milhdbk217f',
 'ramstk.models.programdb.mission',
 'ramstk.models.programdb.mission_phase',
 'ramstk.models.programdb.mode',
 'ramstk.models.programdb.nswc',
 'ramstk.models.programdb.opload',
 'ramstk.models.programdb.opstress',
 'ramstk.models.programdb.pof',
 'ramstk.models.programdb.program_info',
 'ramstk.models.programdb.program_status',
 'ramstk.models.programdb.reliability',
 'ramstk.models.programdb.requirement',
 'ramstk.models.programdb.revision',
 'ramstk.models.programdb.similar_item',
 'ramstk.models.programdb.stakeholder',
 'ramstk.models.programdb.test_method',
 'ramstk.models.programdb.usage_profile',
 'ramstk.models.programdb.validation',
 'ramstk.views',
 'ramstk.views.gtk3',
 'ramstk.views.gtk3.allocation',
 'ramstk.views.gtk3.assistants',
 'ramstk.views.gtk3.books',
 'ramstk.views.gtk3.design_electric',
 'ramstk.views.gtk3.design_electric.components',
 'ramstk.views.gtk3.failure_definition',
 'ramstk.views.gtk3.fmea',
 'ramstk.views.gtk3.function',
 'ramstk.views.gtk3.hardware',
 'ramstk.views.gtk3.hazard_analysis',
 'ramstk.views.gtk3.milhdbk217f',
 'ramstk.views.gtk3.milhdbk217f.components',
 'ramstk.views.gtk3.options',
 'ramstk.views.gtk3.pof',
 'ramstk.views.gtk3.preferences',
 'ramstk.views.gtk3.program_status',
 'ramstk.views.gtk3.reliability',
 'ramstk.views.gtk3.requirement',
 'ramstk.views.gtk3.revision',
 'ramstk.views.gtk3.similar_item',
 'ramstk.views.gtk3.stakeholder',
 'ramstk.views.gtk3.usage_profile',
 'ramstk.views.gtk3.validation',
 'ramstk.views.gtk3.widgets']

package_data = \
{'': ['*']}

install_requires = \
['XlsxWriter>=3.0.1,<4.0.0',
 'lifelines>=0.26.3,<0.27.0',
 'matplotlib>=3.3.4,<4.0.0',
 'openpyxl>=3.0.6,<4.0.0',
 'pandas==1.1.5',
 'psycopg2>=2.8.6,<3.0.0',
 'pycairo>=1.20.0,<2.0.0',
 'pygobject>=3.38,<4.0',
 'pypubsub>=4.0.3,<5.0.0',
 'sortedcontainers>=2.3.0,<3.0.0',
 'sqlalchemy-utils>=0.38.0,<0.39.0',
 'sqlalchemy>=1.3.0,<2.0.0',
 'statsmodels>=0.12.2,<0.13.0',
 'sympy>=1.8.0,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'treelib>=1.5.3,<2.0.0',
 'xlrd>=2.0.1,<3.0.0',
 'xlwt>=1.3.0,<2.0.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['numpy>=1.19,<2.0',
                                                         'scipy>=1.5,<2.0'],
 ':python_version >= "3.7" and python_version < "4.0"': ['numpy>=1.21,<2.0',
                                                         'scipy>=1.6.0,<2.0.0']}

entry_points = \
{'console_scripts': ['ramstk = ramstk.__main__:the_one_ring']}

setup_kwargs = {
    'name': 'ramstk',
    'version': '0.15.10',
    'description': 'A tool to manage RAMS data and analyses.',
    'long_description': '# The RAMS ToolKit (RAMSTK)\n> A ToolKit for **R**eliability, **A**vailability, **M**aintainability, and\n> **S**afety (RAMS) analyses.\n\n<table>\n    <tr>\n        <th>Documentation</th>\n        <td>\n            <a href=\'https://ramstk.readthedocs.io/en/latest/?badge=latest\'><img src=\'https://readthedocs.org/projects/ramstk/badge/?version=latest\' alt=\'Documentation Status\' /></a>\n        </td>\n    </tr>\n    <tr>\n        <th>Tests</th>\n        <td>\n        <img alt="GitHub Workflow Status" src="https://img.shields.io/github/workflow/status/ReliaQualAssociates/ramstk/RAMSTK%20Test%20Suite?label=Build%20%26%20Test">\n        <a href="https://codecov.io/gh/ReliaQualAssociates/ramstk"><img src="https://codecov.io/gh/ReliaQualAssociates/ramstk/branch/master/graph/badge.svg?token=sFOa7EjZAg"/></a>\n        <a href=\'https://coveralls.io/github/ReliaQualAssociates/ramstk?branch=master\'><img src=\'https://coveralls.io/repos/github/ReliaQualAssociates/ramstk/badge.svg?branch=master\' alt=\'Coverage Status\' /></a>\n    </td>\n    </tr>\n    <tr>\n        <th>Quality</th>\n        <td>\n            <a href="https://www.codefactor.io/repository/github/reliaqualassociates/ramstk"><img src="https://www.codefactor.io/repository/github/reliaqualassociates/ramstk/badge" alt="CodeFactor" /></a>\n            <img alt="Quality Gate" src="https://sonarcloud.io/api/project_badges/measure?project=ReliaQualAssociates_ramstk&metric=alert_status">\n        </td>\n    </tr>\n    <tr>\n        <th>Packages</th>\n        <td>\n            <img alt="GitHub release (latest SemVer including pre-releases)" src="https://img.shields.io/github/v/release/ReliaQualAssociates/ramstk?include_prereleases&label=GitHub%20Release">\n            <img alt="PyPI" src="https://img.shields.io/pypi/v/ramstk?label=PyPi%20Release">\n        </td>\n    </tr>\n</table>\n\n## 🚩 Table of Contents\n- [Features](#-features)\n- [Installing](#-installing)\n    - [Prerequisites](#prerequisites)\n    - [Download](#download)\n    - [Running the Tests](#running-the-tests)\n- [Usage](#-usage)\n- [Documentation](#documentation)\n- [Contributing](#-contributing)\n- [Authors](#-authors)\n- [License](#-license)\n- [Similar Products](#similar-products)\n\n## Disclaimer\n\nRAMSTK attempts to use [Semantic Versioning](https://semver.org/) 2.0.0.  Per\n4, major version 0 is for initial development and anything may change at\nany time.  That is certainly the case for RAMSTK!  Because RAMSTK is a one\ndeveloper show, there is no active develop branch at the moment.  This may\nchange after release of 1.0.0.  Until then, tagged releases can be used, but\nthe `latest` tag may not work and may not be backwards-compatible.  While major\nversion is at 0, breaking changes will be reflected in bumps to the minor\nversion number.  That is, version 0.15.0 is not compatible with version 0.14.0.\nAlso at this time, patch versions will not be released.  This will change after\nversion 1.0.0 is released.\n\n## 🎨&nbsp; Features\n\nRAMSTK is built on the concept of modules where a module is a collection of\n related information and/or analyses pertinent to system development.  The\n  modules currently included in RAMSTK are:\n\n* Function Module\n  - Functional decomposition\n  - Hazards analysis\n* Requirements Module\n  - Stakeholder input prioritization\n  - Requirement development\n  - Analysis of requirement for clarity, completeness, consistency, and verifiability\n* Hardware Module\n  - Reliability allocation\n      - Equal apportionment\n      - AGREE apportionment\n      - ARINC apportionment\n      - Feasibility of Objectives\n  - Hardware reliability predictions using various methods\n      - Similar items analysis\n      - MIL-HDBK-217F parts count\n      - MIL-HDBK-217F parts stress\n  - FMEA/FMECA\n      - RPN\n      - MIL-STD-1629A, Task 102 Criticality Analysis\n  - Physics of failure analysis\n* Validation Module\n  - Task description\n  - Task acceptance value(s)\n  - Task time\n  - Task cost\n  - Overall validation plan time/cost estimates\n\n## 💾&nbsp; Installing\n\nThese instructions will hopefully get RAMSTK up and running on your local\nmachine.  RAMSTK uses a Makefile to install/uninstall itself because there are\nvarious icon, data, and configuration files that also need to be installed\noutside site-packages.  Thus, only the actual RAMSTK application is available\nat PyPi and the initial installation must be done using the source asset at\nGitHub for the release you wish to install or cloning the RAMSTK repository if\nyou\'d like the latest code.\n\nRAMSTK uses [postgresql](https://www.postgresql.org/) for its database\n engine.  You\'ll need to have a user with read/write access to a postgresql\n  server to use RAMSTK.\n\n### Download and Install\n\nInstall any missing RAMSTK dependencies using pip, your package manager, and/or\nbuild from source.  Then download the \\<version> of RAMSTK source from GitHub\nyou wish to install.\n\n```shell\n$ wget https://github.com/ReliaQualAssociates/ramstk/archive/v<version>.tar.gz\n$ tar -xf v<version>.tar.gz\n$ cd ramstk-<version>\n$ make install\n```\n\nThe install target recognizes PREFIX=<non-default install path> so you can\n install RAMSTK in your $HOME or a virtual environment.  Since RAMSTK is\n  still a version 0 product, it\'s highly recommended that you install in a\n   virtual environment.\n\n```shell\n$ wget https://github.com/ReliaQualAssociates/ramstk/archive/v<version>.tar.gz\n$ tar -xf v<version>.tar.gz\n$ cd ramstk-<version>\n$ make PREFIX=$VIRTUAL_ENV install\n```\n\nWhen upgrading RAMSTK, you can simply:\n\n```shell\n$ pip install\n```\n\nThis will only install the latest RAMSTK version from PyPi and will leave\nconfiguration, data, and icon files untouched.  If you are using the latest\ncode from GitHub, you can also use the Makefile:\n\n```shell\n$ make install.dev\n```\n\n### Development Dependencies\n\nI use [poetry](https://github.com/python-poetry/poetry) to manage the\ndependencies for RAMSTK while I\'m developing.  Using the Makefile, install as\nfollows:\n\n```shell\n$ make depends\n```\n\nThis should get all the needed development and runtime requirements installed\nif they\'re not already.\n\n### Running the Tests\n\nTo run the entire test suite for RAMSTK after installing, simply execute:\n\n```shell\n$ make test\n```\n\nTo run the test suite with coverage, execute:\n\n```shell\n$ make coverage\n```\n\nTo run specific tests or groups of tests, use pytest:\n\n```shell\n$ pytest -m integration tests/modules/test_allocation.py\n$ pytest -m calculation tests/analyses/prediction\n```\n\n## 🔨&nbsp; Usage\n\nAfter installing RAMSTK, it can be launched from a terminal emulator:\n\n```\n$ ramstk\n```\n\nThis is a good option if you need to file an issue as the output should be\n included in your report.\n\nRAMSTK installs a *.desktop file and can be found where ever applications in\n the category Math or Science are listed.\n\n## Documentation\n\nDocumentation for RAMSTK can be found at [Read the Docs](https://ramstk.readthedocs.io/en/latest) You should check it out!\n\n## 💬&nbsp; Contributing\n\nPlease read [CONTRIBUTING.md](https://github.com/ReliaQualAssociates/ramstk/tree/develop/docs/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.\n\nAlso read [DEVELOPMENT_ENV.md](https://github.com/ReliaQualAssociates/ramstk/tree/develop/docs/DEVELOPMENT_ENV.md) for instructions on setting up a development environment to work on and test RAMSTK.\n\n## 🍞&nbsp; Authors\n\n* **Doyle \'weibullguy\' Rowland** - *Initial work* - [weibullguy](https://github.com/weibullguy)\n\n## 📜&nbsp; License\nThis project is licensed under the BSD-3-Clause License - see the [LICENSE](https://github.com/ReliaQualAssociates/ramstk/blob/develop/LICENSE) file for details.\n\nRAMSTK is also registered with the United States Copyright Office under\n registration number TXu 1-896-035.\n\n## Similar Products\n\nThe following are commercially available products that perform RAMS analyses\n.  We are not endorsing any of them; they are all fine products and may be a\n better fit for you or your organization depending on your needs and budget\n .  Obviously, we would prefer you use RAMSTK.\n\n* [PTC Windchill Quality](https://www.ptc.com/en/products/plm/capabilities/quality)\n* [ReliaSoft Synthesis](https://www.reliasoft.com/products)\n',
    'author': "Doyle 'weibullguy' Rowland",
    'author_email': 'doyle.rowland@reliaqual.com',
    'maintainer': "Doyle 'weibullguy' Rowland",
    'maintainer_email': 'doyle.rowland@reliaqual.com',
    'url': 'https://github.com/ReliaQualAssociates/ramstk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
