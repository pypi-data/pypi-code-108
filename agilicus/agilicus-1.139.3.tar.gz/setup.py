# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['agilicus',
 'agilicus.agilicus_api',
 'agilicus.agilicus_api.api',
 'agilicus.agilicus_api.apis',
 'agilicus.agilicus_api.model',
 'agilicus.agilicus_api.models',
 'agilicus.agilicus_api.test',
 'agilicus.output']

package_data = \
{'': ['*'],
 'agilicus': ['.openapi-generator/*'],
 'agilicus.agilicus_api': ['docs/*']}

install_requires = \
['PyJWT>=2.3.0,<2.4.0',
 'certifi>=14.05.14',
 'click>=7.0.0,<8.0.0',
 'cryptography>=3.1.1,<4.0.0',
 'ipapi==1.0.4',
 'keyring>=23.0.0',
 'oauth2client>=4.1.3,<4.2.0',
 'prettytable>=0.7.2,<0.8.0',
 'python_dateutil>2.5.3',
 'pyyaml==5.4.1',
 'requests>=2.23.0,<3.0.0',
 'six>=1.14.0,<2.0.0']

extras_require = \
{'billing': ['stripe>=2.60.0,<3.0.0', 'prometheus_client==0.11.0']}

entry_points = \
{'console_scripts': ['agilicus-cli = agilicus.main:main']}

setup_kwargs = {
    'name': 'agilicus',
    'version': '1.139.3',
    'description': 'Agilicus SDK',
    'long_description': '## Agilicus SDK (Python)\n\nThe [Agilicus Platform](https://www.agilicus.com/) API [github](https://github.com/Agilicus)\nis defined using [OpenAPI 3.0](https://github.com/OAI/OpenAPI-Specification),\nand may be used from any language. This allows configuration of our Zero-Trust Network Access cloud native platform\nusing REST. You can see the API specification [online](https://www.agilicus.com/api).\n\nThis package provides a Python SDK, class library interfaces for use in\naccessing individual collections. In addition it provides a command-line-interface (CLI)\nfor interactive use.\n\nRead the class-library documentation [online](https://www.agilicus.com/api/)\n\nA subset of this code (that which accesses the above API) is [generated](agilicus/agilicus_api_README.md)\n\nGenerally you may install this as:\n```\npip install --upgrade agilicus\n```\nYou may wish to add bash completion by adding this to your ~/.bashrc:\n```\neval "$(_AGILICUS_CLI_COMPLETE=source agilicus-cli)"\n```\n\n## Build\n\n(first generate the api access, \'cd ..; ./local-build\')\n\n```\npoetry install\npoetry run pre-commit install\npoetry run pytest\n```\n\nTo run the CLI from the development venv:\ngene\n\n`poetry run python -m agilicus.main`\n\nTo format & lint:\n\n```\npoetry run black .\npoetry run flake8\n```\n\n## CLI Usage\n\nCredentials are cached in ~/.config/agilicus, per issuer.\n\n```\nagilicus-cli list-applications\n```\n\n## Debugging with Codium\n\n```\n"python.venvPath": "~/.cache/pypoetry/virtualenvs"\n```\n',
    'author': 'Agilicus Devs',
    'author_email': 'dev@agilicus.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.agilicus.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
