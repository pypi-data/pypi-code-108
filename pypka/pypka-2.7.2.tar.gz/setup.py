# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypka', 'pypka.CHARMM36m', 'pypka.G54A7', 'pypka.clean', 'pypka.mc']

package_data = \
{'': ['*'],
 'pypka.CHARMM36m': ['sts/*'],
 'pypka.G54A7': ['sts/*', 'sts_cphmd/*', 'sts_old/*']}

install_requires = \
['delphi4py>=1.0.1', 'pdbmender>=0.4.0', 'psutil', 'pytest>=6.2.5']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['numpy'],
 ':python_version >= "3.7"': ['numpy>=1.21.0']}

setup_kwargs = {
    'name': 'pypka',
    'version': '2.7.2',
    'description': 'A python module for flexible Poisson-Boltzmann based pKa calculations with proton tautomerism',
    'long_description': '[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mms-fcul/PypKa/blob/master/examples/notebook/pypka.ipynb) [![CircleCI](https://circleci.com/gh/mms-fcul/PypKa.svg?style=svg)](https://circleci.com/gh/mms-fcul/PypKa) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/59a058e4bf0846f18d9d1f6b16a4a0e5)](https://www.codacy.com/gh/mms-fcul/PypKa/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mms-fcul/PypKa&amp;utm_campaign=Badge_Grade) [![Documentation Status](https://readthedocs.org/projects/pypka/badge/?version=latest)](https://pypka.readthedocs.io/en/latest/?badge=latest)\n\n[![PyPI version](https://badge.fury.io/py/pypka.svg)](https://badge.fury.io/py/pypka)  [![PyPI - Downloads](https://img.shields.io/pypi/dm/pypKa)](https://badge.fury.io/py/pypKa)\n\n# PypKa\n\nA python module for flexible Poisson-Boltzmann based pKa calculations with proton tautomerism\nDOI: <a href="https://doi.org/10.1021/acs.jcim.0c00718">10.1021/acs.jcim.0c00718</a>\n\n```bibtex\n@article{reis2020jcim,\nauthor = {Reis, Pedro B. P. S. and Vila-Viçosa, Diogo and Rocchia, Walter and Machuqueiro, Miguel},\ntitle = {PypKa: A Flexible Python Module for Poisson–Boltzmann-Based pKa Calculations},\njournal = {Journal of Chemical Information and Modeling},\nvolume = {60},\nnumber = {10},\npages = {4442-4448},\nyear = {2020},\ndoi = {10.1021/acs.jcim.0c00718}\n}\n```\n\n## Documentation\n\n  Documentation can be found [here](https://pypka.readthedocs.io/en/latest/)\n\n  Starting templates for the the API and CLI usage can be found [here](https://pypka.readthedocs.io/en/latest/example.html) while a online notebook is hosted at [Google Colab](https://colab.research.google.com/github/mms-fcul/PypKa/blob/master/pypka/example/notebook/pypka.ipynb)\n\n\n## Contributing\n\nContributions are encouraged, and they are greatly appreciated!\n\nYou can contribute in many ways:\n\n* Report Bugs\n* Fix Bugs\n* Implement Features\n* Write Documentation\n* Submit Feedback\n\nFor more info check [CONTRIBUTING](./CONTRIBUTING.rst)\n\n## License\n\n  pypka is distributed under a [LGPL-3.0](./LICENSE), however delphi4py depends on\n  DelPhi which is proprietary. To use DelPhi the user is required to\n  download the DelPhi license\n  [here](https://honiglab.c2b2.columbia.edu/software/cgi-bin/software.pl?input=DelPhi)\n\n## Contacts\n\n  Please submit a github issue to report bugs and to request new features.\n  Alternatively you may find the developer [here](mailto:pdreis@fc.ul.pt). Please visit ou [website](http://mms.rd.ciencias.ulisboa.pt/) for more information.\n',
    'author': 'Pedro Reis',
    'author_email': 'pdreis@fc.ul.pt',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypka.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
