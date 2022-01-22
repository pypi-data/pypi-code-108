# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pstock', 'pstock.core', 'pstock.schemas', 'pstock.yahoo_finance']

package_data = \
{'': ['*']}

install_requires = \
['asyncer>=0.0.1,<0.0.2',
 'httpx>=0.21.3,<0.22.0',
 'pandas>=1.3.5,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'tenacity>=8.0.1,<9.0.0']

setup_kwargs = {
    'name': 'pstock-python',
    'version': '0.1.0',
    'description': 'Async python sdk for stock price data.',
    'long_description': '# Pstock\n\nWelcome to pstock documentation.\n\nThis is still a work-in-progess, any help, recommendation or ideas are welcome.\n\nThis packages is for **personal** use only.\n\n## Disclosure\n\nNothing in this project should be considered investment advice. Past performance is not necessarily indicative of future returns.\n\n\n## Documentation\n\nDocumentation is availlable at: [https://obendidi.github.io/pstock/](https://obendidi.github.io/pstock/)\n',
    'author': 'Ouail Bendidi',
    'author_email': 'ouail.bendidi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/obendidi/pstock',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
