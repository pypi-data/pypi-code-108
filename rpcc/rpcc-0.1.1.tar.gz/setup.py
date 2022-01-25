# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rpcc', 'rpcc.console', 'rpcc.transformers', 'rpcc.transformers.cxx17']

package_data = \
{'': ['*'], 'rpcc': ['grammars/*']}

install_requires = \
['lark>=1.0.0,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'rich>=10.15.1,<11.0.0',
 'typing-extensions>=4.0.1,<5.0.0']

entry_points = \
{'console_scripts': ['rpcc = rpcc.__main__:main']}

setup_kwargs = {
    'name': 'rpcc',
    'version': '0.1.1',
    'description': 'A compiler for Mercury-based RPCs',
    'long_description': "# rpcc\n\n**rpcc** is a Python command line tool that allows developers to easily define and work with remote procedure calls (\nRPCs) compatible with the [Mercury](https://mercury-hpc.github.io/) framework.\n\nInspired by Google's [Protocol Buffers](https://developers.google.com/protocol-buffers), **rpcc**\nallows developers to easily define RPCs using a language- and platform- neutral language, that will then be used to\ngenerate all the necessary C/C++ boilerplate code required to actually implement them.\n\n## Documentation\n\nDocumentation for the compiler can be found [here](https://storage.bsc.es/projects/rpcc/).\n",
    'author': 'Alberto Miranda',
    'author_email': 'alberto.miranda@bsc.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://storage.bsc.es/gitlab/hpc/rpcc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
