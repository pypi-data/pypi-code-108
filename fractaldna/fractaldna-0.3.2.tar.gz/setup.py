# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fractaldna',
 'fractaldna.dna_models',
 'fractaldna.structure_models',
 'fractaldna.utils']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.8.2,<5.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.3,<2.0.0',
 'pytest>=6.2.5,<7.0.0',
 'rich>=10.7,<12.0',
 'scipy>=1.7.1,<2.0.0',
 'typer[all]>=0.3.2,<0.5.0']

entry_points = \
{'console_scripts': ['fractaldna = fractaldna.__main__:app']}

setup_kwargs = {
    'name': 'fractaldna',
    'version': '0.3.2',
    'description': 'FractalDNA is a Python package built to generate DNA geometries for simulations',
    'long_description': 'FractalDNA\n===\nPython routines for generating geometric models of DNA\n---\n\n*FractalDNA is being converted to a package, it is under active developmemt*\n\n<div align="center">\n\n[![Build status](https://github.com/natl/fractaldna/workflows/build/badge.svg?branch=master&event=push)](https://github.com/natl/fractaldna/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/fractaldna.svg)](https://pypi.org/project/fractaldna/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/natl/fractaldna/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/natl/fractaldna/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/natl/fractaldna/releases)\n[![License](https://img.shields.io/github/license/natl/fractaldna)](https://github.com/natl/fractaldna/blob/master/LICENSE)\n\n</div>\n\nFractalDNA is a Python package to make DNA geometries that can be joined together like\njigsaw puzzles. Both simple, sections of DNA and Solenoidal DNA can be built. This\nmodule was built to enable DNA-level simulations to be run in [Geant4-DNA](http://geant4-dna.in2p3.fr/), part of the\n[Geant4](geant4.cern.ch/) project.\n\nStructure models define the large scale structure of DNA,\nseeded from fractals. An example seeding fractal is below:\n\n![A 3-D iterated Hilbert Curve](https://raw.githubusercontent.com/natl/fractaldna/master/docs/source/images/fractal-path.svg)\n\nDNA Models provide straight and curved segments that can come together to\nmake DNA for use in simulations.\n\n![A straight solenoidal DNA segment](https://raw.githubusercontent.com/natl/fractaldna/master/docs/source/images/single_solenoid_line_plot.jpg)\n\nProject documentation is available [here](http://natl.github.io/fractaldna/) alongside [notebook examples](http://natl.github.io/fractaldna/examples.html)\n\n## ⚙️ Installation\n\nInstall FractalDNA with `pip`\n\n```bash\npip install fractaldna\n```\n\nor install with `Poetry`\n\n```bash\npoetry add fractaldna\n```\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/natl/fractaldna)](https://github.com/natl/fractaldna/blob/master/LICENSE)\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/natl/fractaldna/blob/master/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{fractaldna,\n  author = {Nathanael Lampe},\n  title = {FractalDNA},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/natl/fractaldna}}\n}\n```\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)',
    'author': 'Nathanael Lampe',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/natl/fractaldna',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
