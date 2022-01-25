# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rdf_linkchecker', 'rdf_linkchecker.checkers']

package_data = \
{'': ['*']}

install_requires = \
['Brotli>=1.0.9,<2.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'rdflib>=6.1.1,<7.0.0',
 'rich>=11.0.0,<12.0.0',
 'typer[all]>=0.4.0,<0.5.0',
 'user-agent>=0.1.10,<0.2.0',
 'validators>=0.18.2,<0.19.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0']}

entry_points = \
{'console_scripts': ['rdf-linkchecker = rdf_linkchecker.__main__:app']}

setup_kwargs = {
    'name': 'rdf-linkchecker',
    'version': '2.0.1',
    'description': 'Awesome `rdf-linkchecker` is a Python cli/package created with https://github.com/TezRomacH/python-package-template',
    'long_description': '# rdf_linkchecker\n\n<div align="center">\n\n[![Build status](https://github.com/WWU-AMM/rdf_linkchecker/workflows/build/badge.svg?branch=main&event=push)](https://github.com/WWU-AMM/rdf_linkchecker/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/rdf_linkchecker.svg)](https://pypi.org/project/rdf_linkchecker/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/WWU-AMM/rdf_linkchecker/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/WWU-AMM/rdf_linkchecker/blob/main/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/WWU-AMM/rdf_linkchecker/releases)\n[![License](https://img.shields.io/github/license/WWU-AMM/rdf_linkchecker)](https://github.com/WWU-AMM/rdf_linkchecker/blob/main/LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\nCheck URLs in Triple-Store files.\n\n</div>\n\n## Installation\n\n```bash\npython3 -m pip install rdf-linkchecker\n```\n\n## Usage\n\nRun with a list of files to check\n\n```bash\nrdf-linkchecker myonefile.ttl myotherfile.ttl\n```\n\n## Configuration\n\nThe `--config-filename` option can be used to pass an `INI`-style file.\n```\n[connection]\nretries = 1\n#seconds\ntimeout = 3\n\n[skip]\n# any URL matching an entry in this comma separated list is not checked\ndomains = https://some.tld/path,http://someother.tld\n\n# level: "all" | "only-failed" | "none"\n# target: "console" | filename\n"reporting": {"level": "all", "target": "console"}\n```\n\n\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'WWU-AMM',
    'author_email': 'rene.fritze@wwu.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/renefritze/rdf-linkchecker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
