# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tree_comments']

package_data = \
{'': ['*']}

install_requires = \
['django-tree-queries>=0.7.0,<0.8.0']

setup_kwargs = {
    'name': 'django-tree-comments',
    'version': '0.0.3',
    'description': 'A django library for building comments in tree structure.',
    'long_description': '# django-tree-comments\n\nA django library for building comments in tree structure.\n\n> This library is under heavy development. v0.0.0 is a placeholder version which actually contains nothing. Version numbers of the library follow [SemVer](https://semver.org/). However, to avoid version numbers grow too fast, at the experimental stage the library will be released under version number with format 0.0.x that SemVer rules do not apply.\n\n## Features\n\n- Query comments as a tree structure efficiently thanks to [django-tree-queries](https://github.com/matthiask/django-tree-queries).\n- No generic relationships, no additional fields needed so that make comment model pure and clean.\n- Provide forms, serializers, utilities and everything you need to help building a complete comment app for your django project.\n\n## Limitations\n\nSince the core feature for tree structure comments is based on the implementation of [django-tree-queries](https://github.com/matthiask/django-tree-queries), so this library extends the same limitations from that.\n\n## Usage\n\nAvailable soon...\n\n## Example project\n\nAvailable soon...',
    'author': 'jukanntenn',
    'author_email': 'jukanntenn@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jukanntenn/django-tree-comments',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
