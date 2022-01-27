# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ansible_pygments', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['pygments>=2.4.0']

entry_points = \
{'pygments.lexers': ['Ansible-output = '
                     'ansible_pygments.lexers:AnsibleOutputLexer',
                     'ansible-output = '
                     'ansible_pygments.lexers:AnsibleOutputLexer'],
 'pygments.styles': ['Ansible = ansible_pygments.styles:AnsibleStyle',
                     'ansible = ansible_pygments.styles:AnsibleStyle']}

setup_kwargs = {
    'name': 'ansible-pygments',
    'version': '0.1.1',
    'description': 'Tools for building the Ansible Distribution',
    'long_description': '# [Pygments] lexer and style Ansible snippets\n\n[![GitHub Actions CI/CD workflow](https://github.com/ansible-community/ansible-pygments/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ansible-community/ansible-pygments/actions/workflows/ci-cd.yml)\n[![Codecov badge](https://img.shields.io/codecov/c/github/ansible-community/ansible-pygments)](https://codecov.io/gh/ansible-community/ansible-pygments)\n\nThis project provides a [Pygments] lexer that is able to handle\n[Ansible] output. It may be used anywhere Pygments is integrated.\nThe lexer is registered globally under the name `ansible-output`.\n\nIt also provides a [Pygments] style for tools needing to highlight\ncode snippets.\n\nThe code is licensed under the terms of the [BSD 2-Clause license].\n\n## Using the lexer in [Sphinx]\n\nMake sure this library in installed in the same env as your [Sphinx]\nautomation via `pip install ansible-pygments sphinx`. Then, you should\nbe able to use a lexer by its name `ansible-output` in the code blocks\nof your RST documents. For example:\n\n```rst\n.. code-block:: ansible-output\n\n    [WARNING]: Unable to find \'/nosuchfile\' in expected paths (use -vvvvv to see paths)\n\n    ok: [localhost] => {\n        "msg": ""\n    }\n```\n\n## Using the style in [Sphinx]\n\nIt is possible to just set `ansible` in `conf.py` and it will "just\nwork", provided that this project is installed alongside [Sphinx] as\nshown above.\n\n```python\npygments_style = \'ansible\'\n```\n\n[Ansible]: https://www.ansible.com/?utm_medium=github-or-pypi&utm_source=ansible-pygments--readme\n[Pygments]: https://pygments.org\n[Sphinx]: https://www.sphinx-doc.org\n[BSD 2-Clause license]: https://opensource.org/licenses/BSD-2-Clause\n',
    'author': 'Felix Fontein',
    'author_email': 'felix@fontein.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ansible-community/ansible-pygments',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.0,<4.0.0',
}


setup(**setup_kwargs)
