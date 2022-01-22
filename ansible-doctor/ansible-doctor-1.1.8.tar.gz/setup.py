# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ansibledoctor']

package_data = \
{'': ['*'], 'ansibledoctor': ['templates/hugo-book/*', 'templates/readme/*']}

install_requires = \
['Jinja2==3.0.3',
 'anyconfig==0.12.0',
 'appdirs==1.4.4',
 'colorama==0.4.4',
 'environs==9.4.0',
 'jsonschema==4.4.0',
 'nested-lookup==0.2.23',
 'pathspec==0.9.0',
 'python-json-logger==2.0.2',
 'ruamel.yaml==0.17.20']

entry_points = \
{'console_scripts': ['ansible-doctor = ansibledoctor.cli:main']}

setup_kwargs = {
    'name': 'ansible-doctor',
    'version': '1.1.8',
    'description': 'Generate documentation from annotated Ansible roles using templates.',
    'long_description': '# ansible-doctor\n\nAnnotation based documentation for your Ansible roles\n\n[![Build Status](https://img.shields.io/drone/build/thegeeklab/ansible-doctor?logo=drone&server=https%3A%2F%2Fdrone.thegeeklab.de)](https://drone.thegeeklab.de/thegeeklab/ansible-doctor)\n[![Docker Hub](https://img.shields.io/badge/dockerhub-latest-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/thegeeklab/ansible-doctor)\n[![Quay.io](https://img.shields.io/badge/quay-latest-blue.svg?logo=docker&logoColor=white)](https://quay.io/repository/thegeeklab/ansible-doctor)\n[![Python Version](https://img.shields.io/pypi/pyversions/ansible-doctor.svg)](https://pypi.org/project/ansible-doctor/)\n[![PyPI Status](https://img.shields.io/pypi/status/ansible-doctor.svg)](https://pypi.org/project/ansible-doctor/)\n[![PyPI Release](https://img.shields.io/pypi/v/ansible-doctor.svg)](https://pypi.org/project/ansible-doctor/)\n[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/ansible-doctor)](https://github.com/thegeeklab/ansible-doctor/graphs/contributors)\n[![Source: GitHub](https://img.shields.io/badge/source-github-blue.svg?logo=github&logoColor=white)](https://github.com/thegeeklab/ansible-doctor)\n[![License: GPL-3.0](https://img.shields.io/github/license/thegeeklab/ansible-doctor)](https://github.com/thegeeklab/ansible-doctor/blob/main/LICENSE)\n\nThis project is based on the idea (and at some parts on the code) of [ansible-autodoc](https://github.com/AndresBott/ansible-autodoc) by Andres Bott so credits goes to him for his work.\n\n_ansible-doctor_ is a simple annotation like documentation generator based on Jinja2 templates. While _ansible-doctor_ comes with a default template called `readme`, it is also possible to write your own templates. This gives you the ability to customize the output and render the data to every format you like (e.g. HTML or XML).\n\n_ansible-doctor_ is designed to work within your CI pipeline to complete your testing and deployment workflow. Releases are available as Python Packages on [GitHub](https://github.com/thegeeklab/ansible-doctor/releases) or [PyPI](https://pypi.org/project/ansible-doctor/) and as Docker Image on [Docker Hub](https://hub.docker.com/r/thegeeklab/ansible-doctor).\n\nYou can find the full documentation at [https://ansible-doctor.geekdocs.de](https://ansible-doctor.geekdocs.de/).\n\n## Contributors\n\nSpecial thanks goes to all [contributors](https://github.com/thegeeklab/ansible-doctor/graphs/contributors). If you would like to contribute,\nplease see the [instructions](https://github.com/thegeeklab/ansible-doctor/blob/main/CONTRIBUTING.md).\n\n## License\n\nThis project is licensed under the GPL-3.0 License - see the [LICENSE](https://github.com/thegeeklab/ansible-doctor/blob/main/LICENSE) file for details.\n',
    'author': 'Robert Kaussow',
    'author_email': 'mail@thegeeklab.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ansible-doctor.geekdocs.de/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
