# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poglossary']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'polib>=1.1.1,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'tabulate[widechars]>=0.8.9,<0.9.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['poglossary = poglossary.poglossary:app']}

setup_kwargs = {
    'name': 'poglossary',
    'version': '0.1.4',
    'description': 'A CLI tool that scans through .po files and searches for mistranslated terms based on user-defined glossary mapping',
    'long_description': '# poglossary\n\n[![Python](https://img.shields.io/pypi/pyversions/poglossary.svg?style=plastic)](https://badge.fury.io/py/poglossary)\n[![PyPI](https://badge.fury.io/py/poglossary.svg)](https://badge.fury.io/py/poglossary)\n\nA CLI tool that scans through translation project (`.po` files) searching for mistranslated terms based on the user-defined glossary mapping.\n\nThis project is specially tailored for [Python Documentation Translation Project (zh_TW)](https://github.com/python/python-docs-zh-tw) but can be applied for all translation projects that adopt Portable Object files (`.po`).\n\n## Install\n\nTo install the current release:\n\n```sh\npip3 install poglossary\n```\n\nTo update it to the latest version, add `--upgrade` flag to the above commands.\n\nRun `poglossary --help` and you should see the following output if it\'s installed sucessfully.\n\n```sh\npoglossary --help\n# Usage: poglossary [OPTIONS] [PATH] [CONFIG_FILE]\n\n#   poglossary: check translated content in .po files based on given translation\n#   mapping\n\n# Arguments:\n#   [PATH]         the path of the directory storing .po files  [default: .]\n#   [CONFIG_FILE]  input mapping file  [default: ./poglossary.yml]\n\n# Options:\n#   --excludes PATH       the directories that need to be omitted\n#   --install-completion  Install completion for the current shell.\n#   --show-completion     Show completion for the current shell, to copy it or\n#                         customize the installation.\n#   --help                Show this message and exit.\n```\n\n## Usage\n\n### Config File\n\nA config file in YAML format is required for poglossary, only the following two keys are recognized:\n\n- `glossary` (required): A mapping of untrnaslated term to translated term. The value can be a list if it has multiple translation choices.\n- `ignore` (optional): If skipping the checking for specific regex patterns or rST syntax is wanted, add the key `patterns` or `rst_tags` as the example below.\n\n```yml\n# Sample config file (.yml)\nglossary:\n  exception: 例外\n  function: 函式\n  instance: 實例\n  type: # can be a list of possible translated terms of "type"\n    - 型別\n    - 種類\n\nignore:\n  patterns:\n    - "type code(s)?" # "type code" or "type codes" will be skipped\n  rst_tags:\n    - source # :source:`*` will be skipped\n    - class\n    - c:\n        - func # :c:func:`*` will be skipped\n        - data\n```\n\nor you can checkout a more detailed configuration in [poglossary.example.yml](./poglossary.example.yml) (, which is the config tend to be used in [pydoc-zhtw](https://github.com/python/python-docs-zh-tw)).\n\n### Command\n\n```shell\npoglossary <source_path> <config_file>\n```\n\n`poglossary` takes in two optional arguments:\n\n- `source_path`: It can be the path of the target PO file or a directory that stores PO files. Defaults to `.`.\n- `config_file`: The path of the config file. Defaults to `./poglossary.yml`.\n\nThe sample output is shown below:\n\n![image](https://user-images.githubusercontent.com/24987826/149608253-bec9d2ed-6605-41c8-956c-5e23e8447a5d.png)\n\n## Todo\n\n- [ ] Functionality\n  - [ ] More handy parameters/options\n- [ ] CI/CD\n  - [ ] Unit tests\n- [ ] Config files\n  - [ ] Handle missing fields.\n  - [ ] Commands for creating a basic config file.\n\n## Acknowledge\n\n`poglossary` is primarily inspired by those fantastic translator tools collected in [poutils](https://github.com/afpy/poutils) and [translate toolkit](https://github.com/translate/translate).\n',
    'author': 'Matt.Wang',
    'author_email': 'mattwang44@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
