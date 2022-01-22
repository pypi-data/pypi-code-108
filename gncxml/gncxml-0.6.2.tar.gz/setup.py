# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gncxml']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.5,<2.0.0']

entry_points = \
{'console_scripts': ['gncxml = gncxml._cli:main']}

setup_kwargs = {
    'name': 'gncxml',
    'version': '0.6.2',
    'description': 'Extract entries from GnuCash data file to pandas.DataFrame.',
    'long_description': '# gncxml\n\n[![PyPI](https://img.shields.io/pypi/v/gncxml)](https://pypi.org/project/gncxml/)\n\ngncxml - extract entries from GnuCash data file to pandas.DataFrame\n\n## Installation\n\n```bash\npip install gncxml\n```\n\n## Usage (Command Line)\n\n```\nusage: gncxml [-h] [-l] [--csv] TYPE [FILE]\n\ngncxml - print entries in GnuCash data file as data frame\n\npositional arguments:\n  TYPE        type of entries to print (account | commodity | price | split |\n              transaction)\n  FILE        GnuCash data file (XML format)\n\noptional arguments:\n  -h, --help  show this help message and exit\n  -l, --long  list in long format\n  --csv       print in csv format\n```\n\n## Usage (Python Module)\n\n```python\nimport sys\nimport gncxml\n\ntry:\n    book = gncxml.Book("mybook.gnucash")\nexcept OSError as err:\n    sys.exit(err)\n\n# Extract splits as pandas.DataFrame\ndf = book.list_splits()\nprint(df[df["trn_date"] >= "2017-10-01"].to_csv())\n```\n\nSee also: [examples/module_usage.ipynb](https://github.com/LiosK/gncxml/blob/master/examples/module_usage.ipynb)\n\n## License\n\nCopyright 2017-2022 LiosK\n\nLicensed under the Apache License, Version 2.0.\n',
    'author': 'LiosK',
    'author_email': 'contact@mail.liosk.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LiosK/gncxml',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.12,<4.0.0',
}


setup(**setup_kwargs)
