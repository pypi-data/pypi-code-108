# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['djlint', 'djlint.formatter']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'pathspec>=0.9.0,<0.10.0',
 'regex>=2022.1.18,<2023.0.0',
 'tomlkit>=0.8.0,<0.9.0',
 'tqdm>=4.62.2,<5.0.0']

extras_require = \
{'test': ['coverage>=6.2,<7.0',
          'pytest>=6.2.5,<7.0.0',
          'pytest-cov>=3.0.0,<4.0.0']}

entry_points = \
{'console_scripts': ['djlint = djlint:main']}

setup_kwargs = {
    'name': 'djlint',
    'version': '0.7.3',
    'description': 'HTML Template Linter and Formatter',
    'long_description': '# ![djLint Logo](https://raw.githubusercontent.com/Riverside-Healthcare/djLint/master/docs/src/static/img/icon.png)\n\nFind common formatting issues and *reformat* HTML templates.\n\n***[Django](https://django.readthedocs.io/en/stable/ref/templates/language.html)\u2003·\u2003[Jinja](https://jinja2docs.readthedocs.io/en/stable/)\u2003·\u2003[Nunjucks](https://mozilla.github.io/nunjucks/)\u2003·\u2003[Twig](https://twig.symfony.com)\u2003·\u2003[Handlebars](https://handlebarsjs.com)\u2003·\u2003[Mustache](http://mustache.github.io/mustache.5.html)\u2003·\u2003[GoLang](https://pkg.go.dev/text/template)***\n\nPs, ``--check`` it out on other templates as well!\n\n[![codecov](https://codecov.io/gh/Riverside-Healthcare/djlint/branch/master/graph/badge.svg?token=eNTG721BAA)](https://codecov.io/gh/Riverside-Healthcare/djlint) [![test](https://github.com/Riverside-Healthcare/djlint/actions/workflows/test.yml/badge.svg)](https://github.com/Riverside-Healthcare/djlint/actions/workflows/test.yml) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/dba6338b0e7a4de896b45b382574f369)](https://www.codacy.com/gh/Riverside-Healthcare/djlint/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Riverside-Healthcare/djlint&amp;utm_campaign=Badge_Grade) [![Maintainability](https://api.codeclimate.com/v1/badges/5febe4111a36c7e0d2ed/maintainability)](https://codeclimate.com/github/Riverside-Healthcare/djlint/maintainability) [![Downloads](https://pepy.tech/badge/djlint)](https://pepy.tech/project/djlint)[![chat](https://img.shields.io/badge/chat-discord-green)](https://discord.gg/taghAqebzU) [![PyPI](https://img.shields.io/pypi/v/djlint)](https://pypi.org/project/djlint/)\n\n## Documentation\n\nRead the [documentation](https://djlint.com)\n\n## Installation and Usage\n\n**djLint** can be installed with `pip install djlint`, and is easy to run:\n\n```sh\n# to lint a directory\ndjlint /path\n\n# to lint a directory with custom extension\ndjlint /path -e html.dj\n\n# to check formatting on a file\ndjlint /path/file.html.j2 --check\n\n# to reformt a directory without printing the file diff\ndjlint /path --reformat --quiet\n\n# using stdin\necho "<div></div>" | djlint -\n\n```\n\n## Show your format\n\nAdd a badge to your projects ```readme.md```:\n\n```md\n[![Code style: djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://github.com/Riverside-Healthcare/djlint)\n```\n\nAdd a badge to your ```readme.rst```:\n\n```rst\n.. image:: https://img.shields.io/badge/html%20style-djlint-blue.svg\n   :target: https://github.com/Riverside-Healthcare/djlint\n```\nLooks like this:\n\n[![djLint](https://img.shields.io/badge/html%20style-djLint-blue.svg)](https://github.com/Riverside-Healthcare/djlint)\n\n\n## Contributing\n\nSend a pr with a new feature, or checkout the [issue](https://github.com/Riverside-Healthcare/djlint/issues) list and help where you can.\n',
    'author': 'Christopher Pickering',
    'author_email': 'cpickering@rhc.net',
    'maintainer': 'Christopher Pickering',
    'maintainer_email': 'cpickering@rhc.net',
    'url': 'https://github.com/Riverside-Healthcare/djlint',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
