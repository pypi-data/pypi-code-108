# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prometheuspvesd']

package_data = \
{'': ['*']}

install_requires = \
['anyconfig==0.12.0',
 'appdirs==1.4.4',
 'colorama==0.4.4',
 'environs==9.4.0',
 'jsonschema==4.4.0',
 'nested-lookup==0.2.23',
 'prometheus-client==0.12.0',
 'proxmoxer==1.2.0',
 'python-json-logger==2.0.2',
 'requests==2.27.1',
 'ruamel.yaml==0.17.20']

entry_points = \
{'console_scripts': ['prometheus-pve-sd = prometheuspvesd.cli:main']}

setup_kwargs = {
    'name': 'prometheus-pve-sd',
    'version': '1.1.9',
    'description': 'Prometheus Service Discovery for Proxmox VE.',
    'long_description': "# prometheus-pve-sd\n\nPrometheus Service Discovery for Proxmox VE\n\n[![Build Status](https://img.shields.io/drone/build/thegeeklab/prometheus-pve-sd?logo=drone&server=https%3A%2F%2Fdrone.thegeeklab.de)](https://drone.thegeeklab.de/thegeeklab/prometheus-pve-sd)\n[![Docker Hub](https://img.shields.io/badge/dockerhub-latest-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/thegeeklab/prometheus-pve-sd)\n[![Quay.io](https://img.shields.io/badge/quay-latest-blue.svg?logo=docker&logoColor=white)](https://quay.io/repository/thegeeklab/prometheus-pve-sd)\n[![Python Version](https://img.shields.io/pypi/pyversions/prometheus-pve-sd.svg)](https://pypi.org/project/prometheus-pve-sd/)\n[![PyPI Status](https://img.shields.io/pypi/status/prometheus-pve-sd.svg)](https://pypi.org/project/prometheus-pve-sd/)\n[![PyPI Release](https://img.shields.io/pypi/v/prometheus-pve-sd.svg)](https://pypi.org/project/prometheus-pve-sd/)\n[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/prometheus-pve-sd)](https://github.com/thegeeklab/prometheus-pve-sd/graphs/contributors)\n[![Source: GitHub](https://img.shields.io/badge/source-github-blue.svg?logo=github&logoColor=white)](https://github.com/thegeeklab/prometheus-pve-sd)\n[![License: MIT](https://img.shields.io/github/license/thegeeklab/prometheus-pve-sd)](https://github.com/thegeeklab/prometheus-pve-sd/blob/main/LICENSE)\n\nThis project provides a simple custom service discovery for [Prometheus](https://prometheus.io/). It is using the Proxmox PVE API to fetch Hosts and it's meta information to generate a Prometheus compatible [file based](https://prometheus.io/docs/guides/file-sd/) service discovery. Releases are available as Python Packages on [GitHub](https://github.com/thegeeklab/prometheus-pve-sd/releases) or [PyPI](https://pypi.org/project/prometheus-pve-sd/) and as Docker Image on [Docker Hub](https://hub.docker.com/r/thegeeklab/prometheus-pve-sd).\n\nYou can find the full documentation at [https://prometheus-pve-sd.geekdocs.de](https://prometheus-pve-sd.geekdocs.de).\n\n## Contributors\n\nSpecial thanks goes to all [contributors](https://github.com/thegeeklab/prometheus-pve-sd/graphs/contributors). If you would like to contribute,\nplease see the [instructions](https://github.com/thegeeklab/prometheus-pve-sd/blob/main/CONTRIBUTING.md).\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](https://github.com/thegeeklab/prometheus-pve-sd/blob/main/LICENSE) file for details.\n",
    'author': 'Robert Kaussow',
    'author_email': 'mail@thegeeklab.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thegeeklab/prometheus-pve-sd/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
