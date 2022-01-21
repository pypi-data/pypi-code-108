# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magic', 'magic.shared']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.0,<9.0.0',
 'fastjsonschema>=2.15.0,<3.0.0',
 'importlib-metadata>=4.6.3,<5.0.0']

entry_points = \
{'console_scripts': ['magic = magic:main']}

setup_kwargs = {
    'name': 'tatuarvela-magic',
    'version': '3.1.2',
    'description': 'A tool for simplifying repeated command line tasks',
    'long_description': '# ![Magic icon](./icon.png?raw=true "Magic icon") Magic\n\n[![Repository](https://img.shields.io/badge/repository-gray.svg?logo=github)](https://github.com/TatuArvela/magic)\n[![GitHub issues](https://img.shields.io/github/issues/TatuArvela/magic)](https://github.com/TatuArvela/magic/issues)\n[![Pipeline status](https://github.com/TatuArvela/magic/actions/workflows/verify.yml/badge.svg?event=push)](https://github.com/TatuArvela/magic/actions/workflows/verify.yml)\n[![PyPI](https://img.shields.io/pypi/v/tatuarvela-magic)](https://pypi.org/project/tatuarvela-magic/)\n[![License](https://img.shields.io/github/license/TatuArvela/magic)](https://github.com/TatuArvela/magic/blob/master/LICENSE)\n[![Created at Nitor](https://img.shields.io/badge/created%20at-Nitor-informational.svg)](https://nitor.com/)\n\nMagic is a tool for turning repeated command line tasks and long, hard to\nremember commands into quickly callable simple commands, **spells**.\n\nSpells provide a simple and managed alternative to manually created aliases or\nscripts.\n\n## 🏃 Quick tour\n\n1. To add spells, run the built-in **wizard** `magic add`\n2. Spells are written into the **spellbook** file (`~/.spellbook.json`)\n3. Each spell is available as a command under `magic`, which can be listed\n   with `magic --help`\n4. A spell can have one or several command names, which are called **magic\n   words**  \n   e.g. `magic build-app` and `magic ba`\n5. Spells can have **arguments** passed to them  \n   e.g. `magic say abra kadabra`\n\n## 💻 Installation\n\nMagic is designed for macOS and common Linux distributions using Bash or Zsh.\nMagic also works on Windows Subsystem for Linux.\n\nMagic requires Python 3.7 or above, and can be installed using pip:\n\n```console\npython3 -m pip install tatuarvela-magic\n```\n\n## 🪄 Usage\n\n```console\n$ magic\n✨ Magic v3.1.2 © 2021 Tatu Arvela\nA tool for simplifying repeated command line tasks\n\nUsage: magic [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  -h, --help  Show this message and exit.\n\nCommands:\n  add      Add spell to spellbook\n  e        Example echo spell with arguments \'$a0\' and \'$a1\'\n  edit     Open spellbook in editor\n  example  Example echo spell with arguments \'$a0\' and \'$a1\'\n```\n\nEditing the spellbook is currently done with an external editor (**Visual Studio\nCode** by default).\n\n## 📚 Documentation\n\n### Spell options\n\nSpell options can be listed with the `-h` or `--help` option.\n\n```console\n$ magic example --help\nUsage: magic example [OPTIONS]\n\n  Example echo spell with arguments \'$a0\' and \'$a1\'\n\nOptions:\n  -d, --delete  Delete this spell.\n  -s, --show    Show details of this spell.\n  -h, --help    Show this message and exit.\n```\n\n`-d` or `--delete` option can be used to delete a spell.\n\n`-s` or `--show` option can be used to show the details of a spell.\n\nOther options are interpreted as arguments for spells.\n\n### Spell arguments\n\nSpells can have an array of arguments, which are populated according to their\nindex, starting from 0.\n\nExample:\n\n```json\n{\n  "description": "Example echo spell with arguments \'$a0\' and \'$a1\'",\n  "magicWords": [\n    "e",\n    "example"\n  ],\n  "commands": [\n    "echo $a0",\n    "echo $a1"\n  ],\n  "argumentCount": 2\n}\n```\n\n```console\n$ magic example cat dog\n✨ Example echo spell with arguments \'cat\' and \'dog\'\ncat\ndog\n✅ 12:30:43 | ⏱ 0:00:00\n```\n\nThe arguments can be used in the spell description and commands.\n\nThe description arguments are replaced when displaying the spell message.\n\n`argumentCount` property is automatically inferred from the description and\ncommands.\n\nExcessive usage of arguments is considered to be an anti-pattern, it is\nrecommended to create separate spells instead.\n\n#### Advanced usage: Empty arguments\n\nArgument are handled as an ordered array. If necessary, it is possible to make\nan argument an empty string: `\'\'`.\n\n### Messages\n\n#### Message\n\nMagic can print the description of a spell, filled with the provided arguments\n\n```console\n✨ Example echo spell with arguments \'cat\' and \'dog\'\n```\n\n`showMessage` property defaults to `true`.\n\n#### Success message\n\nMagic can show a success message which reports the starting time and duration of\na spell. This may be useful for longer operations.\n\n```console\n✅ 23:46:43 | ⏱ 0:00:00\n```\n\n`showSuccessMessage` property defaults to `true`.\n\n## ⚙️ Development\n\nDevelopment instructions and notes can be found\nin [DEVELOPMENT.md](./DEVELOPMENT.md)\n',
    'author': 'Tatu Arvela',
    'author_email': 'tatu.arvela@nitor.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TatuArvela/magic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
