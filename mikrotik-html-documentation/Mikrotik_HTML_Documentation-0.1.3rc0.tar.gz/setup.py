# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mt_html']

package_data = \
{'': ['*']}

install_requires = \
['RouterOS-api==0.17.0',
 'click>=8.0.3,<9.0.0',
 'json2html>=1.3.0,<2.0.0',
 'python-dotenv>=0.19.2,<0.20.0']

entry_points = \
{'console_scripts': ['mt-html = mt_html.cli:cli']}

setup_kwargs = {
    'name': 'mikrotik-html-documentation',
    'version': '0.1.3rc0',
    'description': 'Mikrotik Config to Markup',
    'long_description': "# Mikrotik HTML Dumper\n\n---\n\nThis is a small project written since my team worked with mikrotiks and we sometimes needed to present audits of the configuration for upper manangement in a quick and easy to read format.\n\n## Installing\n\nYou can use pip to install this script\n\n```pip install mikrotik_html_documentation```\n\n## General Use\n\nOne installed, you can see the options available to you by running the help parameter\n\n```bash\nmt-html --help\nUsage: mt-html [OPTIONS] COMMAND [ARGS]...\n\n  This simple tool logins to a Mikrotik and creats an HTML dump\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  dump\n  env\n```\n\n## Requirements\n\nYou'll need to setup a .env file for the username and password. You can do so by running the following command\n\n```mt-html generate-env```\n\nIt will then ask you to enter the username and password which will be stored in a .env file for you from the current working directory of the script.\n\n\n# Usage\n\n---\n\nTo use the script, simply run the following\n\n```mt-html html-dump -f <firewall>```\n\nIt will then ask you to enter the IP or FQDN of the firewall and dump out HTML code so you can easily upload to markup language supported documentation systems, or simply share it as a web file.\nFiles are created and can be located in your home directory\n\n```~/mikrotik_html_dump```\n\n# License\n\n---\n\nApache-2.0\n\n\n\n\n",
    'author': 'Angelo Poggi',
    'author_email': 'angelo.poggi@opti9tech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/purplecomputer/Mikrotik_HTML_Documentation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
