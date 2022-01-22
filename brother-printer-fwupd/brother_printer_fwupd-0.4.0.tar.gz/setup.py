# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brother_printer_fwupd']

package_data = \
{'': ['*']}

install_requires = \
['BeautifulSoup4>=4.9.1,<5.0.0',
 'lxml>=4.6.2,<5.0.0',
 'pysnmp>=4.4.12,<5.0.0',
 'requests>=2.23.0,<3.0.0',
 'termcolor>=1.1.0,<2.0.0']

extras_require = \
{'autodiscover': ['zeroconf>=0.28.7,<0.29.0'],
 'graphical': ['Gooey>=1.0.3,<2.0.0']}

entry_points = \
{'console_scripts': ['brother_printer_fwupd = '
                     'brother_printer_fwupd.__main__:main']}

setup_kwargs = {
    'name': 'brother-printer-fwupd',
    'version': '0.4.0',
    'description': 'Script to update the firmware of some Brother printers (e. g. MFC).',
    'long_description': None,
    'author': 'sedrubal',
    'author_email': 'dev@sedrubal.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sedrubal/brother_printer_fwupd.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
