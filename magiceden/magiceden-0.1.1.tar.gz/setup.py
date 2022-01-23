# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magiceden']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'selenium>=4.1.0,<5.0.0',
 'webdriver-manager>=3.5.2,<4.0.0']

setup_kwargs = {
    'name': 'magiceden',
    'version': '0.1.1',
    'description': 'A scraper based API for Magic Eden, a Solana based NFT marketplace.',
    'long_description': "# Installation\n\n```\npip install magiceden\n```\n\n# Usage\n\nFind the slug of the NFT collection you're interested in by referencing the suffix of the collection URL.\n\nExample: https://magiceden.io/marketplace/solana_monkey_business\n\n```\nfrom magiceden import MagicEdenScraper\n\nclient = MagicEdenScraper()\n\nprint(client.get_floor_price('solana_monkey_business'))\nprint(client.get_total_volume('solana_monkey_business'))\nprint(client.get_avg_price('solana_monkey_business'))\n```",
    'author': 'Sumer Malhotra',
    'author_email': 'sumermalhotra1998@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
