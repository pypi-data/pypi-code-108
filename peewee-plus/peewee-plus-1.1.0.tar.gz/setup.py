# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tests']

package_data = \
{'': ['*']}

modules = \
['peewee_plus']
install_requires = \
['peewee>=3.14.8,<4.0.0']

setup_kwargs = {
    'name': 'peewee-plus',
    'version': '1.1.0',
    'description': 'Various extensions, helpers, and utilities for Peewee',
    'long_description': '# peewee+\n\nVarious extensions, helpers, and utilities for [Peewee](http://peewee-orm.com)\n\n[![PyPI Version](https://img.shields.io/pypi/v/peewee-plus)](https://pypi.org/project/peewee-plus/)\n[![License](https://img.shields.io/pypi/l/peewee-plus)](https://opensource.org/licenses/MIT)\n[![Python Supported Versions](https://img.shields.io/pypi/pyversions/peewee-plus)](https://www.python.org)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nSee the [Changelog](https://github.com/enpaul/peewee-plus/blob/devel/CHANGELOG.md) for\nrelease history.\n\n## Documentation\n\n*The documentation for this project is currently a work in progress. Please see the source code for complete docs*\n\n- [Installing](#installing)\n- [Features](#features)\n- [For Developers](#for-developers)\n\n## Installing\n\nPeewee+ is [available on PyPI](https://pypi.org/project/peewee-plus/) and can be installed\nusing Poetry, Pipenv, or Pip:\n\n```bash\n# Using poetry\npoetry add peewee-plus\n\n# Using pipenv\npipenv install peewee-plus\n\n# Using pip\npython -m venv peewee\nsource peewee/bin/activate\npython -m pip install peewee-plus\n```\n\nOnce installed, Peewee+ can be imported like below:\n\n```python\nimport peewee_plus\n```\n\n## Features\n\n### Constants\n\n`SQLITE_DEFAULT_PRAGMAS` - The default pragmas to use with an SQLite database connection,\ntaken directly from the\n[Peewee docs](http://docs.peewee-orm.com/en/latest/peewee/database.html#recommended-settings).\n\n`SQLITE_DEFAULT_VARIABLE_LIMIT` - The maximum number of variables an SQL query can use\nwhen using SQLite\n\n### Functions\n\n[`calc_batch_size`](https://github.com/enpaul/peewee-plus/blob/1.0.0/peewee_plus.py#L71) -\nHelper function for determining how to batch a create/update query with SQLite\n\n[`flat_transaction`](https://github.com/enpaul/peewee-plus/blob/devel/peewee_plus.py#L137)\n\\- Decorator function for wrapping callables in a database transaction without creating\nnested transactions\n\n### Classes\n\n[`PathField`](https://github.com/enpaul/peewee-plus/blob/1.0.0/peewee_plus.py#179) - A\nPeewee database field for storing\n[Pathlib](https://docs.python.org/3/library/pathlib.html) objects, optionally relative to\na runtime value.\n\n[`PrecisionFloatField`](https://github.com/enpaul/peewee-plus/blob/1.0.0/peewee_plus.py#L237)\n\\- A Peewee database field for storing floats while specifying the\n[MySQL precision parameters](https://dev.mysql.com/doc/refman/8.0/en/floating-point-types.html)\n`M` and `D`\n\n[`JSONField`](https://github.com/enpaul/peewee-plus/blob/1.0.0/peewee_plus.py#L267) - A\nPeewee database field for storing arbitrary JSON-serializable data\n\n[`EnumField`](https://github.com/enpaul/peewee-plus/blob/1.0.0/peewee_plus.py#L322) - A\nPeewee database field for storing Enums by name\n\n## For Developers\n\nAll project contributors and participants are expected to adhere to the\n[Contributor Covenant Code of Conduct, v2](CODE_OF_CONDUCT.md) ([external link](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)).\n\nThe `devel` branch has the latest (and potentially unstable) changes. The stable releases\nare tracked on [Github](https://github.com/enpaul/peewee-plus/releases),\n[PyPi](https://pypi.org/project/peewee-plus/#history), and in the\n[Changelog](CHANGELOG.md).\n\n- To report a bug, request a feature, or ask for assistance, please\n  [open an issue on the Github repository](https://github.com/enpaul/peewee-plus/issues/new).\n- To report a security concern or code of conduct violation, please contact the project\n  author directly at **\u200cme \\[at\u200c\\] enp dot\u200e \u200cone**.\n- To submit an update, please\n  [fork the repository](https://docs.github.com/en/enterprise/2.20/user/github/getting-started-with-github/fork-a-repo)\n  and [open a pull request](https://github.com/enpaul/peewee-plus/compare).\n\nDeveloping this project requires at least [Python 3.7](https://www.python.org/downloads/)\nand at least [Poetry 1.0](https://python-poetry.org/docs/#installation). GNU Make can\noptionally be used to quickly setup a local development environment, but this is not\nrequired.\n\nTo setup a local development environment:\n\n```bash\n# Clone the repository...\n# ...over HTTPS\ngit clone https://github.com/enpaul/peewee-plus.git\n# ...over SSH\ngit clone git@github.com:enpaul/peewee-plus.git\n\ncd peewee-plus/\n\n# Create and configure the local dev environment\nmake dev\n\n# See additional make targets\nmake help\n```\n',
    'author': 'Ethan Paul',
    'author_email': '24588726+enpaul@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/enpaul/peewee-plus/',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
