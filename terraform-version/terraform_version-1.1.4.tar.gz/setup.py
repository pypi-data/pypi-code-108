# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['terraform_version']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'terraform-version',
    'version': '1.1.4',
    'description': 'Package for tracking existing Terraform versions',
    'long_description': None,
    'author': 'Josh Wycuff',
    'author_email': 'Joshua.Wycuff@turner.com',
    'maintainer': 'Josh Wycuff',
    'maintainer_email': 'Joshua.Wycuff@turner.com',
    'url': 'https://github.com/joshwycuff/python-terraform-utils/packages/terraform_version',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
