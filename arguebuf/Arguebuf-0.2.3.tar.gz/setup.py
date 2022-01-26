# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arguebuf']

package_data = \
{'': ['*']}

install_requires = \
['arg-services>=0.1.18,<0.2.0',
 'graphviz>=0.13.2,<0.14.0',
 'lxml>=4.6,<5.0',
 'networkx>=2.4,<3.0',
 'pendulum>=2.0,<3.0']

extras_require = \
{'docs': ['sphinx>=3.5,<4.0',
          'sphinx-rtd-theme>=0.5.2,<0.6.0',
          'furo>=2021.4.11b34,<2022.0.0',
          'myst-parser>=0.13.7,<0.14.0']}

setup_kwargs = {
    'name': 'arguebuf',
    'version': '0.2.3',
    'description': 'A library for loading argument graphs in various formats (e.g., AIF).',
    'long_description': '# Argument Buffers (Arguebuf)\n\n- [Documentation](https://arguebuf.readthedocs.io/en/latest/)\n- [PyPI](https://pypi.org/project/arguebuf/)\n',
    'author': 'Mirko Lenz',
    'author_email': 'info@mirko-lenz.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://recap.uni-trier.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
