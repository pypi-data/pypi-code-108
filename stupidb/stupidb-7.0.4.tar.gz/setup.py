# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stupidb',
 'stupidb.associative',
 'stupidb.functions',
 'stupidb.functions.associative',
 'stupidb.functions.navigation',
 'stupidb.functions.ranking',
 'stupidb.tests']

package_data = \
{'': ['*']}

install_requires = \
['atpublic>=2.3,<3.0', 'tabulate>=0.8.9,<0.9.0', 'toolz>=0.11,<0.12']

extras_require = \
{'animation': ['pydot>=1.4.2,<2.0.0']}

setup_kwargs = {
    'name': 'stupidb',
    'version': '7.0.4',
    'description': 'The stupidest of all the databases.',
    'long_description': '# StupiDB\n\n[![PyPI](https://img.shields.io/pypi/v/stupidb.svg)](https://pypi.python.org/pypi/stupidb)\n[![CI](https://github.com/cpcloud/stupidb/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cpcloud/stupidb/actions/workflows/ci.yml)\n[![Docs](https://readthedocs.org/projects/stupidb/badge/?version=latest)](https://stupidb.readthedocs.io/en/latest/?badge=latest)\n\nPronounced in at least two ways:\n\n1. Stoo-PID-eh-bee, rhymes with "stupidity"\n2. Stoopid-DEE-BEE, like "stupid db"\n\nAre you tired of software that\'s too smart? Try StupiDB, the stupidest database\nyou\'ll ever come across.\n\nStupiDB was built to understand how a relational database might be implemented.\n\nRDBMSs like PostgreSQL are extremely complex. It was hard for to me to imagine\nwhat implementing the core of a relational database like PostgreSQL would look\nlike just by tinkering with and reading the source code, so I decided to write\nmy own.\n\n## Features\n\n- Stupid joins\n- Idiotic window functions\n- Woefully naive set operations\n- Sophomoric group bys\n- Dumb custom aggregates\n- Scales down, to keep expectations low\n- Wildly cloud unready\n- Worst-in-class performance\n\n## Non-Features\n\n- Stupid simple in-memory format: `Iterable[Mapping[str, Any]]`\n- Stupidly clean codebase\n\n## Credits\n\nThis package was created with\n[Cookiecutter](https://github.com/audreyr/cookiecutter) and the\n[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)\nproject template.\n',
    'author': 'Phillip Cloud',
    'author_email': 'cpcloud@gmail.com',
    'maintainer': 'Phillip Cloud',
    'maintainer_email': 'cpcloud@gmail.com',
    'url': 'https://github.com/cpcloud/stupidb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
