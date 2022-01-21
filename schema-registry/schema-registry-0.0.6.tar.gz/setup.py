# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['schema_registry',
 'schema_registry.app',
 'schema_registry.app.business',
 'schema_registry.app.ui',
 'schema_registry.registries']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'jsonschema>=4.3.2,<5.0.0',
 'lxml>=4.7.1,<5.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dotenv>=0.19,<0.20',
 'requests-toolbelt>=0.9,<0.10',
 'requests>=2,<3',
 'rich>=10,<11',
 'typer>=0,<1']

extras_require = \
{'docs': ['sphinx<4',
          'sphinx-click>=2.7.1,<3.0.0',
          'sphinx-rtd-theme>=0.5.2,<0.6.0',
          'sphinx-autodoc-typehints>=1.12.0,<2.0.0']}

entry_points = \
{'console_scripts': ['schemareg = schema_registry.app.ui.cli:app']}

setup_kwargs = {
    'name': 'schema-registry',
    'version': '0.0.6',
    'description': 'A schema registry implementation. Should you need to keep your json schemas in one place.',
    'long_description': '# Schema Registry\n\nJust a project stub for now\n\nContributions are welcome. Just get in touch.\n\n## Quickstart\n\nSimply `pip install schema-registry` and get going.\n\n## Development\n\nThis project uses `poetry` for dependency management and `pre-commit` for local checks.\n',
    'author': 'Eduard Thamm',
    'author_email': 'eduard.thamm@thammit.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/friendly-facts/schema-registry',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
