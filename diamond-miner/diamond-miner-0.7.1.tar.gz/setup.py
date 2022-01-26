# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['diamond_miner', 'diamond_miner.generators', 'diamond_miner.queries']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.6.5,<4.0.0',
 'pygfc>=1.0.3,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'zstandard>=0.15.2,<0.17.0']

setup_kwargs = {
    'name': 'diamond-miner',
    'version': '0.7.1',
    'description': 'High-speed, Internet-scale, load-balanced paths discovery.',
    'long_description': '# Diamond-Miner 💎\n\n[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/diamond-miner/Tests?logo=github)](https://github.com/dioptra-io/diamond-miner/actions/workflows/tests.yml)\n[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/diamond-miner?logo=codecov&logoColor=white&token=RKZSQ2CL4J)](https://app.codecov.io/gh/dioptra-io/diamond-miner)\n[![Documentation](https://img.shields.io/badge/documentation-online-blue.svg?logo=read-the-docs&logoColor=white)](https://dioptra-io.github.io/diamond-miner/)\n[![PyPI](https://img.shields.io/pypi/v/diamond-miner?logo=pypi&logoColor=white)](https://pypi.org/project/diamond-miner/)\n\n> D-Miner is the first Internet-scale system that captures a multipath view of the topology.\n> By combining and adapting state-of-the-art multipath detection and high speed randomized topology discovery techniques,\n> D-Miner permits discovery of the Internet’s multipath topology in 2.5 days[^1] when probing at 100kpps.[^2]\n\n## 🚀 Quickstart\n\nDiamond-Miner is implemented as a Python library which computes the probes to send.\nTo actually send the probes, we recommend [Caracal](https://github.com/dioptra-io/caracal) but you can use the tool of your liking, such as [yarrp](https://github.com/cmand/yarrp) or [scamper](https://www.caida.org/catalog/software/scamper/) as long as you convert its output to the expected format described in the documentation.\n\nTo get started, install Diamond-Miner and head over to the [documentation](https://dioptra-io.github.io/diamond-miner/):\n```bash\npip install diamond-miner\n```\n\n## Publications\n\nDiamond-Miner has been presented and published at [NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/vermeulen).\nSince then, the code has been refactored and separated in the [`diamond-miner`](https://github.com/dioptra-io/diamond-miner) and [`caracal`](https://github.com/dioptra-io/caracal) repositories.\nThe code as it was at the time of the publication is available in the [`diamond-miner-cpp`](https://github.com/dioptra-io/diamond-miner-cpp) and [`diamond-miner-wrapper`](https://github.com/dioptra-io/diamond-miner-wrapper) repositories.\n\nIf you use Diamond-Miner, please cite the following paper:\n```bibtex\n@inproceedings {DiamondMiner2020,\n  author = {Kevin Vermeulen and Justin P. Rohrer and Robert Beverly and Olivier Fourmaux and Timur Friedman},\n  title = {Diamond-Miner: Comprehensive Discovery of the Internet{\\textquoteright}s Topology Diamonds },\n  booktitle = {17th {USENIX} Symposium on Networked Systems Design and Implementation ({NSDI} 20)},\n  year = {2020},\n  isbn = {978-1-939133-13-7},\n  address = {Santa Clara, CA},\n  pages = {479--493},\n  url = {https://www.usenix.org/conference/nsdi20/presentation/vermeulen},\n  publisher = {{USENIX} Association},\n  month = feb,\n}\n```\n\n## Authors\n\nDiamond-Miner is developed and maintained by the [Dioptra group](https://dioptra.io) at [Sorbonne Université](https://www.sorbonne-universite.fr) in Paris, France.\nThe initial version has been written by [Kévin Vermeulen](https://github.com/kvermeul), with subsequents refactoring and improvements by [Maxime Mouchet](https://github.com/maxmouchet) and [Matthieu Gouel](https://github.com/matthieugouel).\n\n## License & Dependencies\n\nThis software is released under the [MIT license](/LICENSE), in accordance with the license of its dependencies.\n\nName                                             | License                                                      | Usage\n-------------------------------------------------|--------------------------------------------------------------|------\n[pygfc](https://github.com/maxmouchet/gfc)       | [MIT](https://opensource.org/licenses/MIT)                   | Generating random permutations\n[python-zstandard](https://github.com/indygreg/python-zstandard) | [3-clause BSD](https://opensource.org/licenses/BSD-3-Clause) | Compression\n[requests](https://github.com/psf/requests) | [Apache 2.0](https://opensource.org/licenses/Apache-2.0)     | Querying the database\n[scamper](https://github.com/cmand/scamper) | [3-Clause BSD](https://opensource.org/licenses/BSD-3-Clause) | Reading and writing warts\n\n[^1]: As of v0.1.0, diamond-miner can discover the multipath topology in less than a day when probing at 100k pps.\n[^2]: Vermeulen, Kevin, et al. ["Diamond-Miner: Comprehensive Discovery of the Internet\'s Topology Diamonds."](https://www.usenix.org/system/files/nsdi20-paper-vermeulen.pdf) _17th USENIX Symposium on Networked Systems Design and Implementation (NSDI 20)_. 2020.\n',
    'author': 'Kevin Vermeulen',
    'author_email': 'kevin.vermeulen@columbia.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dioptra-io/diamond-miner',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}
from build_ext import *
build(setup_kwargs)

setup(**setup_kwargs)
