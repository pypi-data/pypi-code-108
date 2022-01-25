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
 'rich>=10.7.0,<11.0.0',
 'scipy>=1.7.1,<2.0.0',
 'typer[all]>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['fractaldna = fractaldna.__main__:app']}

setup_kwargs = {
    'name': 'fractaldna',
    'version': '0.2.0',
    'description': 'Awesome `fractaldna` is a Python cli/package created with https://github.com/TezRomacH/python-package-template',
    'long_description': 'fractaldna\n===\nPython routines for generating simple models of DNA\n---\n\n*FractalDNA is being converted to a package, it is under active developmemt*\n\n<div align="center">\n\n[![Build status](https://github.com/fractaldna/fractaldna/workflows/build/badge.svg?branch=master&event=push)](https://github.com/fractaldna/fractaldna/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/fractaldna.svg)](https://pypi.org/project/fractaldna/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/fractaldna/fractaldna/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/fractaldna/fractaldna/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/fractaldna/fractaldna/releases)\n[![License](https://img.shields.io/github/license/fractaldna/fractaldna)](https://github.com/fractaldna/fractaldna/blob/master/LICENSE)\n\n</div>\n\nThis repository is an offshoot of my thesis work, where I simulate the impact\nof ionising radiation on DNA. For this, I need to model and visualise very\nlarge DNA structures\n\nModelling DNA geometries computationally can be done very crudely based on\na few DNA motifs and a fractal geometry. It provides a memory efficient way of\nensuring that an appropriate density of DNA is placed in a sample volume. The\nidea is to use a fractal as a seed for a collection of turned and straight\ngeometries, and then place repeating turned and straight DNA segments inside\nthese geometries.\n\nHere you can see the idea being applied to the first few iterations of a Hilbert\ncurve.\n\n![Fractal DNA](https://cloud.githubusercontent.com/assets/2887977/22364141/936da1ee-e46f-11e6-9c56-ee4e0dcb8d0f.png)\n\nThe project is divided into three sections, each with their own Readme:\n* `hilbert3d` provides routines for generating 3D fractals from L-systems.\n* `simpledna` has some routines for generating simple turned and straight\nDNA models.\n* `vis` contains some Python routines that work in Blender to visualise the\nwhole DNA structure.\n\nThis project is currently in a beta form, I\'m working on documentation and\nthe ability to generate videos of DNA procedurally in Blender from Python\nscripts. Though at the moment you can get some decent still results from the\nvisualisation tools:\n\n![DNA in Blender](https://cloud.githubusercontent.com/assets/2887977/22364140/936c16d0-e46f-11e6-9e71-ed8c512663ea.png)\n\n_____\n\nAlso, a shout out to the blender DNA example by George Lydecker where\nI first saw Blender being used to render DNA, and whose example code\ninspired some of what is here. (https://github.com/glydeck/MoloculeParser)\n',
    'author': 'fractaldna',
    'author_email': 'hello@fractaldna.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fractaldna/fractaldna',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
