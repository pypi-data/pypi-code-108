# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resume_as_code']

package_data = \
{'': ['*']}

install_requires = \
['Cerberus>=1.3,<2.0',
 'Jinja2>=3,<4',
 'PyYAML>=6,<7',
 'docxtpl>=0.15.2,<0.16.0',
 'python-docx>=0.8.11,<0.9.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'python-magic>=0.4.24,<0.5.0',
 'requests>=2.27.1,<3.0.0',
 'validators>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'resume-as-code',
    'version': '0.0.3',
    'description': 'A tool for automatic resume generation based on Jinja-Word-templates and YAML-files',
    'long_description': None,
    'author': 'Tim Van Erum',
    'author_email': 'tim.vanerum@dataroots.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.0,<4.0.0',
}


setup(**setup_kwargs)
