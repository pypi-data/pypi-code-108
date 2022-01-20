# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['phisherman']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'taskipy>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'phisherman.py',
    'version': '1.0.0',
    'description': 'Async API Wrapper for Phisherman.gg in Python',
    'long_description': '<h1 align="center">Phisherman.py</h1>\n<h3 align="center">\nAsynchronous Python API Wrapper for phisherman.gg\n</h3>\n\n<!-- Badges. -->\n<p align="center">\n<a href="https://pypi.org/project/phisherman.py">\n    <img height="20" alt="PyPI version" src="https://img.shields.io/pypi/v/phisherman.py">\n</a>\n\n<a href="https://pypi.org/project/flake8/">\n    <img height="20" alt="Flake badge" src="https://img.shields.io/badge/code%20style-flake8-blue.svg">\n</a>\n\n<a href="https://qristalabs.github.io/phisherman.py">\n    <img height="20" alt="Documentation status" src="https://img.shields.io/badge/documentation-up-00FF00.svg">\n</a>\n</p>\n\n## Installation\n\n**Python 3.8 or above is required**\n\n```sh\n# Stable\npip install phisherman.py\n\n# Development\npip install git+https://github.com/QristaLabs/phisherman.py\n```\n\n## Example\n\n```python\nimport asyncio\nfrom phisherman import Client\n\napp = Client(token="Your Token")\n\nasync def main():\n    if await app.check_domain("internetbadguys.com"):\n        print("Detected suspicious.")\n\n    await app.close()\n\nasyncio.run(main())\n```\n\n## Links\n\n- [Documentation](https://qristalabs.github.io/phisherman.py)\n- [Phisherman](https://phisherman.gg)\n- [API Support Server](https://discord.gg/8sPG4m84Vb)\n',
    'author': 'Vedrecide',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/QristaLabs/phisherman.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
