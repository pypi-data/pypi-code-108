# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rin', 'rin.gateway', 'rin.models', 'rin.rest', 'rin.types']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'typing-extensions>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'rin',
    'version': '0.1.1',
    'description': 'A successor to the Lefi project',
    'long_description': '# Rin\nA strongly typed discord API wrapper.\nThis is the successor to the Lefi project.\n\n## Installation\n\n1. Poetry\n\n   ```\n   poetry add git+https//github.com/an-dyy/Rin\n   ```\n\n2. Pip\n   ```\n   pip install git+https//github.com/an-dyy/Rin\n   ```\n\n## Example(s)\n[Here!](examples/)\n\n## Documentation\n[Documentation](https://rin.readthedocs.io/en/latest/index.html)\n\n## Contributing\n1. If you plan on contributing please open an issue beforehand\n2. Fork the repo, and setup the poetry env (with dev dependencies)\n3. Install pre-commit hooks (*makes it a lot easier for me*)\n    ```\n    pre-commit install\n    ```\n\n## Notable contributors\n\n- [blanketsucks](https://github.com/blanketsucks) - collaborator\n- [an-dyy](https://github.com/an-dyy) - creator and maintainer\n\n[![Discord!](https://img.shields.io/badge/Discord-Rin-blue)](https://discord.gg/ZcAqDBaxRf)\n',
    'author': 'an-dyy',
    'author_email': 'andy.development@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/an-dyy/Rin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
