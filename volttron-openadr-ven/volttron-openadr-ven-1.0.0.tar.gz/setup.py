# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['volttron_openadr_ven']

package_data = \
{'': ['*']}

install_requires = \
['black>=21.5b2,<22.0',
 'mypy>=0.812,<0.813',
 'openleadr>=0.5.24,<0.6.0',
 'pre-commit>=2.13.0,<3.0.0',
 'volttron-client>=0.3.8,<0.4.0']

setup_kwargs = {
    'name': 'volttron-openadr-ven',
    'version': '1.0.0',
    'description': 'A Volttron agent that acts as a Virtual End Node (VEN) within the OpenADR 2.0b specification.',
    'long_description': None,
    'author': 'Mark Bonicillo',
    'author_email': 'mark.bonicillo@pnnl.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
