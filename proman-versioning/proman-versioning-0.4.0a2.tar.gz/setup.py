# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['versioning', 'versioning.grammars']

package_data = \
{'': ['*'], 'versioning': ['templates/*']}

install_requires = \
['argufy>=0.1.1-alpha.12,<0.2.0',
 'cffi>=1.15.0,<2.0.0',
 'compendium>=0.1.1-beta.0,<0.2.0',
 'lark-parser>=0.10.0,<0.11.0',
 'packaging>=21.3,<22.0',
 'pygit2>=1.6.1,<2.0.0',
 'transitions>=0.8.4,<0.9.0']

entry_points = \
{'console_scripts': ['version = versioning.__main__:main']}

setup_kwargs = {
    'name': 'proman-versioning',
    'version': '0.4.0a2',
    'description': 'Project Manager Versioning tool.',
    'long_description': '# Proman Versioning\n\n[![License](https://img.shields.io/badge/License-MPL%202.0-blue.svg)](https://spdx.org/licenses/MPL-2.0)\n[![Build Status](https://travis-ci.org/kuwv/proman-versioning.svg?branch=master)](https://travis-ci.org/kuwv/proman-versioning)\n[![codecov](https://codecov.io/gh/kuwv/proman-versioning/branch/master/graph/badge.svg)](https://codecov.io/gh/kuwv/proman-versioning)\n\n## Overview\n\nProject Manager Versioning is a PEP-440 compliant tool for automating project\nversions using conventional commits.\n\n## Install\n\n`pip install proman-versioning`\n\n## Setup\n\nThis tool is designed to work with any textfile using a templating pattern and\n path to the file.\n\n### Configuring versions\n\nConfiguration can be performed with either the `.versioning` or `pyproject.toml`\nfiles.\n\n#### Global configuration settings:\n\nSpecific types of releases can be disabled by setting the respective release to\nfalse.\n\nDisable development releases:\n```\nenable_devreleases = false\n```\n\nDisable pre-releases:\n```\nenable_prereleases = false\n```\n\nDisable post-releases:\n```\nenable_postreleases = false\n```\n\n#### File specific settings:\n\nUse different version compatibiliy type:\n```\ncompat = "semver"\n```\n\nUpdate only the release version for a configuration:\n```\nrelease_only = true\n```\n\n#### Example `.versioning`\n\nThe `.versioning` config is a non-specfile based project file using TOML. This is the\npreferred configuration for non-python projects that may use this tool.\n\n```\n[proman]\nversion = "1.2.3"\n\n[proman.versioning]\ndisable_devreleases = true\n\n[[tool.proman.versioning.files]]\nfilepath = "pyproject.toml"\npattern = "version = \\"${version}\\""\n\n[[proman.versioning.files]]\nfilepath = "example/__init__.py"\npattern = "__version__ = \'${version}\'"\n```\n\n#### Example `pyproject.toml`\n\n```\n[tool.proman]\nversion = "1.2.3"\n\n[tool.proman.versioning]\n\n[[tool.proman.versioning.files]]\nfilepath = "pyproject.toml"\npattern = "version = \\"${version}\\""\n\n[[tool.proman.versioning.files]]\nfilepath = "example/__init__.py"\npattern = "__version__ = \'${version}\'"\n```\n\n#### Example `setup.cfg`\n\nSetuptools allows `setup.cfg` to pull the version from the application. This\nshould be used in tandem with either of the above configurations to control\nversions for a project.\n\n```\n[metadata]\nname = example\nversion = attr: src.VERSION\n...\n```\n\n## References\n\n- https://www.conventionalcommits.org/en/v1.0.0/\n- https://www.python.org/dev/peps/pep-0440/\n- https://semver.org\n- https://calver.org\n',
    'author': 'Jesse P. Johnson',
    'author_email': 'jpj6652@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
