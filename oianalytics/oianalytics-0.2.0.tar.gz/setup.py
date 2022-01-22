# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oianalytics',
 'oianalytics.api',
 'oianalytics.models',
 'oianalytics.models._template_resources']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.4,<2.0.0', 'pydantic>=1.9.0,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'oianalytics',
    'version': '0.2.0',
    'description': 'Python tools for working with OIAnalytics',
    'long_description': None,
    'author': 'Optimistik SAS',
    'author_email': 'arthur.martel@optimistik.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
