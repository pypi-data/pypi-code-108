# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pytest_pyppeteer']

package_data = \
{'': ['*']}

install_requires = \
['cssselect>=1.1.0,<2.0.0',
 'lxml>=4.7.1,<5.0.0',
 'pyppeteer>=1.0.2,<2.0.0',
 'pytest>=6.2.5,<7.0.0']

entry_points = \
{'pytest11': ['niotest_framework = pytest_pyppeteer.plugin']}

setup_kwargs = {
    'name': 'pytest-pyppeteer',
    'version': '0.3.0',
    'description': 'A plugin to run pyppeteer in pytest',
    'long_description': None,
    'author': 'Luiz Yao',
    'author_email': 'luizyao@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
