# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ip-link', 'ip-link.bezier', 'ip-link.rtgraph3d']

package_data = \
{'': ['*'],
 'ip-link': ['D3js/*', 'moowheel/*', 'scatterplot/*'],
 'ip-link.rtgraph3d': ['rtg/*']}

install_requires = \
['Pillow>=9.0.0,<10.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pypacker>=5.1,<6.0']

setup_kwargs = {
    'name': 'ip-link',
    'version': '0.4.1',
    'description': 'Visualizing the relationships between different IP from network traffic capture.',
    'long_description': '# IP-Link\n\n## Presentation\n\nThe goal of [IP-Link](https://git.sr.ht/~cedric/ip-link)\nis to see the relationships between different IP from network traffic capture,\nthus quickly for a given address with the IP that communicates the most.\nIP-Link offers several visualization methods.\n\n\n## Installation\n\nPython >= 3.8.\n\n```bash\n$ sudo apt install libpcap0.8\n$ git clone https://git.sr.ht/~cedric/ip-link\n$ cd ip-link/\n$ poetry install\n$ poetry shell\n```\n\n## Quick example\n\n```bash\n$ mkdir captures data\n$ sudo tcpdump -p -i enp5s0 -s 0 -w captures/snif.pcap\n$ ip-link/pcap_to_object.py -i captures/snif.pcap -o data/dic.pyobj\n$ ip-link/object_to_graphviz.py -i ./data/dic.pyobj\n$ dot -Tpng -o ./data/graphviz.png ./data/ip.dot\n$ xdg-open ./data/graphviz.png &\n```\n\n\n\n## Tutorial and examples\n\nThe site of IP-Link provides a complete\n[tutorial](https://ip-link.readthedocs.io/en/latest/tutorial.html).\n\n\n## License\n\nThis software is licensed under\n[GNU General Public License version 3](https://www.gnu.org/licenses/gpl-3.0.html).\n\nCopyright (C) 2010-2022 [Cédric Bonhomme](https://www.cedricbonhomme.org).\n',
    'author': 'Cédric Bonhomme',
    'author_email': 'cedric@cedricbonhomme.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sr.ht/~cedric/ip-link',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
