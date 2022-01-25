# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['__init__']
setup_kwargs = {
    'name': 'hexlet-immutable-fs-trees',
    'version': '0.1.8',
    'description': 'File System Tree',
    'long_description': "# python-immutable-fs-trees\n\n[![github action status](https://github.com/hexlet-components/python-immutable-fs-trees/workflows/Python%20CI/badge.svg)](https://github.com/hexlet-components/python-immutable-fs-trees/actions)\n\n## Install\n\n```shell\npip install hexlet-immutable-fs-trees\n```\n\n## Usage example\n\n```python\n\n>>> import hexlet.fs as fs\n>>> fs.is_file(fs.mkfile('config'))\nTrue\n>>> fs.is_directory(fs.mkdir('etc'))\nTrue\n>>> tree = fs.mkdir('etc', [fs.mkfile('config'), fs.mkfile('hosts')])\n>>> children = fs.get_children(tree)\n>>> fs.get_name(children[0])\n'config'\n>>> list(map(lambda item: fs.get_name(item), children))\n['config', 'hosts']\n>>>\n```\n\n[![Hexlet Ltd. logo](https://raw.githubusercontent.com/Hexlet/assets/master/images/hexlet_logo128.png)](https://ru.hexlet.io/pages/about)\n\nThis repository is created and maintained by the team and the community of Hexlet, an educational project. [Read more about Hexlet (in Russian)](https://ru.hexlet.io/pages/about?utm_source=github&utm_medium=link&utm_campaign=python-immutable-fs-trees).\n\nSee most active contributers on [hexlet-friends](https://friends.hexlet.io/).\n",
    'author': 'Hexlet Team',
    'author_email': 'info@hexlet.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hexlet-components/python-immutable-fs-trees',
    'package_dir': package_dir,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
