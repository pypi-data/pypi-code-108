# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iservscrapping']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.6,<4.0.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'lxml>=4.7.1,<5.0.0',
 'markdownify>=0.10.2,<0.11.0',
 'requests-cache>=0.9.1,<0.10.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'iservscrapping',
    'version': '6.0.2',
    'description': 'This Scrapper can get data from iserv servers hosting Untis plans. (Common in germany)',
    'long_description': None,
    'author': 'niwla23',
    'author_email': 'alwin@cloudserver.click',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
