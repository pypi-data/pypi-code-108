# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nv', 'nv.tables', 'nv.tables.implementations']

package_data = \
{'': ['*']}

install_requires = \
['nv-utils>=0.3.0a,<0.4.0']

extras_require = \
{'all': ['openpyxl>=3.0.9,<4.0.0',
         'xlrd>=2.0.1,<3.0.0',
         'xlwt>=1.3.0,<2.0.0',
         'xlutils>=2.0.0,<3.0.0'],
 'xls': ['xlrd>=2.0.1,<3.0.0', 'xlwt>=1.3.0,<2.0.0', 'xlutils>=2.0.0,<3.0.0'],
 'xlsx': ['openpyxl>=3.0.9,<4.0.0']}

setup_kwargs = {
    'name': 'nv-tables',
    'version': '0.1.1',
    'description': 'Tools for read and write data from and into table files (e.g. xls, xlsx, csv, etc.)',
    'long_description': "# nv.tables\nTools for parsing data from and into table formats (CSV, XLS and XLSX)\n\n## What's inside?\n[to come]\n\n## Disclaimers\nTHIS IS UNDOCUMENTED WORK IN PROGRESS. READ THE LICENSE AND USE IT AT YOUR OWN RISK.\n\nTHIS IS STILL A BETA AND BREAKING CHANGES MAY (AND PROBABLY WILL) OCCUR UNTIL ITS CONTENT STABILIZES. WE\nARE ACTIVELY MIGRATING STUFF OUT OF THIS LIBRARY (AND LOOKING FOR SUBSTITUTES THAT ARE MORE ACTIVELY MAINTAINED)\n",
    'author': 'Gustavo Santos',
    'author_email': 'gustavo@next.ventures',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gstos/nv-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
