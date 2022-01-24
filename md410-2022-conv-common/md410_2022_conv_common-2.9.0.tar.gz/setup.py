# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['md410_2022_conv_common']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.20.3,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'docker>=5.0.3,<6.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'redmail>=0.2.0,<0.3.0',
 'rich>=11.0.0,<12.0.0']

setup_kwargs = {
    'name': 'md410-2022-conv-common',
    'version': '2.9.0',
    'description': 'Common libraries for applications related to the 2022 Lions MD410 Convention',
    'long_description': '# Introduction\n\nCommon libraries for applications related to the 2022 Lions Multiple District 410 Convention.\n\n# Associated Applications\n\nSee [this Gitlab group](https://gitlab.com/md410_2022_conv) for associated applications.\n',
    'author': 'Kim van Wyk',
    'author_email': 'vanwykk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/md410_2022_conv/md410_2022_conv_common',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
