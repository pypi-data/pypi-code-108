# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nv',
 'nv.utils',
 'nv.utils.collections',
 'nv.utils.collections.mappings',
 'nv.utils.collections.sequences',
 'nv.utils.collections.structures',
 'nv.utils.decorators',
 'nv.utils.introspect',
 'nv.utils.parsers',
 'nv.utils.parsers.core',
 'nv.utils.parsers.formatters',
 'nv.utils.parsers.string',
 'nv.utils.serializers',
 'nv.utils.typing']

package_data = \
{'': ['*']}

extras_require = \
{'all': ['msgpack-python>=0.5.6,<0.6.0',
         'xmltodict>=0.12.0,<0.13.0',
         'dicttoxml>=1.7.4,<2.0.0',
         'charset-normalizer>=2.0.10,<3.0.0'],
 'detect': ['charset-normalizer>=2.0.10,<3.0.0'],
 'msgpack': ['msgpack-python>=0.5.6,<0.6.0'],
 'xml': ['xmltodict>=0.12.0,<0.13.0', 'dicttoxml>=1.7.4,<2.0.0']}

setup_kwargs = {
    'name': 'nv-utils',
    'version': '0.3.0a20',
    'description': 'Parsers, formatters, data structures and helpers for Python 3 (>=3.9)',
    'long_description': "# nv.utils\nParsers, formatters, data structures and other helpers for Python 3. This is a source of recurring\nportions of reusable code that we needed in our applications, such as tools for configuration parsing,\nvalue casting, data structures, etc.\n\n## What's inside?\n[to come]\n\n\n## Important message on Python for v0.2 and Python < 3.9\nSubstantial changes have been made on the organization of nv-utils for the long run, with breaking changes vs. 0.1.15.\n\n## Disclaimers\nTHIS IS UNDOCUMENTED WORK IN PROGRESS. READ THE LICENSE AND USE IT AT YOUR OWN RISK.\n\nTHIS IS STILL A BETA AND BREAKING CHANGES MAY (AND PROBABLY WILL) OCCUR UNTIL ITS CONTENT STABILIZES. WE\nARE ACTIVELY MIGRATING STUFF OUT OF THIS LIBRARY (AND LOOKING FOR SUBSTITUTES THAT ARE MORE ACTIVELY MAINTAINED)\n",
    'author': 'Gustavo Santos',
    'author_email': 'gustavo@next.ventures',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gstos/nv-utils',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
