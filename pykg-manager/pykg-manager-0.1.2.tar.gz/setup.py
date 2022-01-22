# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['_tbnf',
 '_tbnf.FableSedlex',
 '_tbnf.fable_modules',
 '_tbnf.fable_modules.fable_library',
 'pykg']

package_data = \
{'': ['*']}

install_requires = \
['diskcache>=5.4.0,<6.0.0',
 'dulwich>=0.20.30,<0.21.0',
 'lark>=0.11.3,<0.12.0',
 'loguru>=0.5.3,<0.6.0',
 'tomli-w>=1.0.0,<2.0.0',
 'typing-extensions>=4.0.1,<5.0.0',
 'wisepy2>=1.2.1,<2.0.0',
 'z3-solver>=4.8.14,<5.0.0']

entry_points = \
{'console_scripts': ['pykg = pykg.cli_apis:main']}

setup_kwargs = {
    'name': 'pykg-manager',
    'version': '0.1.2',
    'description': 'A proposal Fable Python package manager',
    'long_description': '## Pykg\n\nA package manager maintains local/remote dependencies for Fable Python projects.\n\nWrite F# and run Python code!\n\n## Installation\n\n```shell\npip install pykg-manager\n```\n\n## Usage\n\n```shell\n> pykg new myproj && cd myproj\n# or mkdir myproj && cd myproj && pykg new .\n\n> cat ./project.comf\n\nproject {\n  name "fspy/testv"\n  mirror "https://raw.githubusercontent.com/thautwarm/comf-index/main"\n  version v0.1.0\n  builder null\n  src {\n    "src/main.fs"\n  }\n  dep {\n    name "lang/python"\n    version ^ v3.8.0\n  }\n  dep {\n    name "lang/net"\n    version >= v5.0.0&&< v7.0.0\n  }\n  exe "src.main"\n}\n\n> cat src/main.fs\nmodule Main\n\nlet _ = printfn "hello world"\n\n> pykg a # resolge packages, compile F# sources, and run main\n\nhello world\n```\n\n',
    'author': 'thautwarm',
    'author_email': 'twshere@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thautwarm/reflect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
