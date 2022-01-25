# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cleaning_utils']

package_data = \
{'': ['*']}

install_requires = \
['datetime',
 'khayyam',
 'numpy',
 'pandas',
 'python-dateutil',
 'pytz',
 'urllib3>=1.26.4,<2.0.0']

extras_require = \
{':python_version < "3.7"': ['importlib_metadata>=4.5.0,<5.0.0']}

setup_kwargs = {
    'name': 'cleaning-utils',
    'version': '0.0.1',
    'description': 'cleaning-utils is a collection of small Python functions and classes for formatting persian texts.',
    'long_description': '<div align="center">\n\n# cleaning-utils\n\n\n[![cleaning-utils version](assets/images/cleaning-utils.svg)](https://github.com/rezashabrang/cleaning-utils)\n[![Python Version](https://img.shields.io/pypi/pyversions/cleaning-utils.svg)](https://pypi.org/project/cleaning-utils/)\n[![coverage report](assets/images/coverage.svg)](.logs/coverage.txt)\n[![static analysis](assets/images/mypy.svg)](.logs/mypy.txt)\n[![vulnerabilities](assets/images/vulnerabilities.svg)](.logs/safety.txt)\n[![lint report](assets/images/pylint.svg)](.logs/pylint-log.txt)\n[![Dependencies Status](assets/images/dependencies.svg)](.logs/dependencies.txt)\n\n[![interrogate](assets/images/interrogate_badge.svg)](.logs/docstring.txt)\n[![maintainability](assets/images/maintainability.svg)](.logs/maintainability.txt)\n[![complexity](assets/images/complexity.svg)](.logs/complexity.txt)\n[![Code style: black](assets/images/codestyle.svg)](https://github.com/psf/black)\n[![Security: bandit](assets/images/security.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](assets/images/precommits.svg)](.pre-commit-config.yaml)\n[![License](https://img.shields.io/github/license/rezashabrang/cleaning-utils)](https://github.com/rezashabrang/cleaning-utils/blob/master/LICENSE)\n\ncleaning-utils is a collection of small Python functions and classes which make\ncleaning pipelines shorter and easier.\n\n</div>\n\n## Install\n\n\n```bash\npip3 install cleaning-utils\n```\n\n## Contributing\n\n### Testing:\n\n```bash\nmake install\nmake test && make coverage && make check-codestyle && make mypy && make check-safety && make extrabadges\n```\n\n### Checks on various versions:\n\n```bash\npython3.8 -m venv .venv_38\n. .venv_38/bin/activate\npython3 -m pip install --upgrade pip\nmake install\nmake test && make coverage && make check-codestyle && make mypy && make check-safety\ndeactivate\n\npython3.9 -m venv .venv_39\n. .venv_39/bin/activate\npython3 -m pip install --upgrade pip\nmake install\nmake test && make coverage && make check-codestyle && make mypy && make check-safety\ndeactivate\n```\n\n\n### Build Package:\n\n```BASH\npre-commit run --all-files\n```\n\nFirst, change the `version` in [`setup.py`](setup.py),  [`pyproject.toml`](pyproject.toml), and change the\n`__version__` in [`__init__.py`](cleaning_utils/__init__.py). Then:\n\n```bash\npython3 setup.py sdist bdist_wheel\n```\n\n### Commit Changes:\n\n```bash\npre-commit run --all-files\ngit add .\ngit commit -m ":sparkles: new feature"\ngit pull\ngit push -u origin master\n```\n\n### Make a release:\n\n```bash\ngit tag -a <write the version e.g., v0.1.2> -m "message of release"\ngit push --tags\nmake release\n```\n\n### Commit Changes to [`README.md`](README.md):\n\n```bash\npre-commit run --all-files\ngit add .\ngit commit -m ":books: README.md updated"\ngit pull\ngit push -u origin master\n```\n\n<div>\nIcon made from\n<a href="http://www.onlinewebfonts.com/icon">\nIcon Fonts\n</a>\nis licensed by CC BY 3.0\n</div>\n\n\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'aasaam',
    'author_email': 'beygi.ma@iums.ac.ir',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rezashabrang/cleaning-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
