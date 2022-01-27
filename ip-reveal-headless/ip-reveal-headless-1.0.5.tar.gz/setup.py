# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ip_reveal_headless',
 'ip_reveal_headless.config',
 'ip_reveal_headless.config.arguments',
 'ip_reveal_headless.tools',
 'ip_reveal_headless.tools.arguments',
 'ip_reveal_headless.tools.logging']

package_data = \
{'': ['*'], 'ip_reveal_headless': ['.idea/*', '.idea/inspectionProfiles/*']}

install_requires = \
['humanize>=3.1.0,<4.0.0',
 'inspy_logger==2.1a14',
 'inspyre-toolbox>=1.2a1,<2.0',
 'inspyred_print>=1.0,<2.0',
 'johnnydep>=1.10,<2.0',
 'pypattyrn>=1.2,<2.0',
 'requests>=2.25.0,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'urllib3>=1.26.8,<2.0.0']

entry_points = \
{'console_scripts': ['ip-reveal = ip_reveal_headless:main',
                     'ip-reveal-headless = ip_reveal_headless:main']}

setup_kwargs = {
    'name': 'ip-reveal-headless',
    'version': '1.0.5',
    'description': 'Quickly ascertain your public IP address, hostname, and local IP address.',
    'long_description': None,
    'author': 'Taylor B.',
    'author_email': 'tayjaybabee@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
