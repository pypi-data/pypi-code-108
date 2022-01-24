# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['modelbase',
 'modelbase.core',
 'modelbase.ode',
 'modelbase.ode.integrators',
 'modelbase.ode.models',
 'modelbase.ode.simulators',
 'modelbase.ode.utils',
 'modelbase.sbml',
 'modelbase.utils']

package_data = \
{'': ['*']}

install_requires = \
['black>=21.11b0,<22.0',
 'ipywidgets>=7.6.5,<8.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'python-libsbml>=5.19.0,<6.0.0',
 'scipy>=1.7.2,<2.0.0',
 'sympy>=1.9,<2.0',
 'tqdm>=4.62.3,<5.0.0',
 'typing-extensions>=4.0.0,<5.0.0']

setup_kwargs = {
    'name': 'modelbase',
    'version': '1.5.4',
    'description': 'A package to build metabolic models',
    'long_description': '# modelbase\n\n[![pipeline status](https://gitlab.com/qtb-hhu/modelbase-software/badges/master/pipeline.svg)](https://gitlab.com/qtb-hhu/modelbase-software/-/commits/master)\n[![coverage report](https://gitlab.com/qtb-hhu/modelbase-software/badges/master/coverage.svg)](https://gitlab.com/qtb-hhu/modelbase-software/-/commits/master)\n[![Documentation Status](https://readthedocs.org/projects/modelbase/badge/?version=latest)](https://modelbase.readthedocs.io/en/latest/?badge=latest)\n[![PyPi](https://img.shields.io/pypi/v/modelbase)](https://pypi.org/project/modelbase/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n[![Downloads](https://pepy.tech/badge/modelbase)](https://pepy.tech/project/modelbase)\n\nmodelbase is a python package to help you build and analyze dynamic mathematical models of biological systems. It has originally been designed for the simulation of metabolic systems, but can be used for virtually any processes, in which some substances get converted into others.\n\nmodelbase incorporates an easy construction method to define \'reactions\'. A rate law and the stoichiometry need to be specified, and the system of differential equations is assembled automatically.\n\nmodelbase allows \'algebraic modules\', which are useful to implement rapid equilibrium or quasi steady-state approximations. In the simplest instance, they allow easy incorporation of conserved quantities.\n\nmodelbase also allows a simple construction of isotope-specific models. This class contains a constructor method that automatically construct all isotope specific versions of a particular reaction. Very cool - check it out!\n\n## Release notes\n\nVersions 1.0 and 0.4.0 introduced changes not compatible with the previous official\nrelease 0.2.5. API changes are summarised in [this notebook](docs/source/api-changes.ipynb)\n\n[Version 0.4.5](https://gitlab.com/qtb-hhu/modelbase-software/-/tags/0.4.5) was the prior stable version\n\n[Version 0.2.5](https://gitlab.com/qtb-hhu/modelbase-software/-/tags/initial-release)\nis the official release for the submission of the\nmansucript "Building mathematical models of biological systems\nwith modelbase, a Python package for semi-automatic ODE assembly\nand construction of isotope-specific models" to the Journal of Open\nResearch Software.\n\nSee changelog.md for details on changes of earlier versions.\n\n## Installation\n\nIf you quickly want to test out modelbase, or do not require assimulo support, install modelbase via\n\n```bash\npip install modelbase\n```\n\nTo enable assimulo support, the easiest way is to install modelbase via conda. We also recommend using the conda-forge channels.\n\n```bash\n# recommended to avoid package clashes\nconda config --add channels conda-forge\n\n# Create a new environment (not necessary, but recommended)\nconda create -n mb39 python=3.9\nconda install -c conda-forge modelbase\n```\n\n## License\n\n[GPL 3](https://gitlab.com/qtb-hhu/modelbase-software/blob/master/LICENSE)\n\n## Documentation\n\nThe official documentation is hosted on [ReadTheDocs](https://modelbase.readthedocs.io/en/latest/).\n\n## Issues and support\n\nIf you experience issues using the software please contact us through our [issues](https://gitlab.com/qtb-hhu/modelbase-software/issues) page.\n\n## Contributing to modelbase\n\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome. See our [contribution guide](https://gitlab.com/qtb-hhu/modelbase-software/blob/master/CONTRIBUTING.md) for more information.\n\n## How to cite\n\nIf you use this software in your scientific work, please cite [this article](https://rdcu.be/ckOSa):\n\nvan Aalst, M., Ebenhöh, O. & Matuszyńska, A. Constructing and analysing dynamic models with modelbase v1.2.3: a software update. BMC Bioinformatics 22, 203 (2021)\n\n- [doi](https://doi.org/10.1186/s12859-021-04122-7)\n- [bibtex file](https://gitlab.com/qtb-hhu/modelbase-software/blob/master/citation.bibtex)\n',
    'author': 'Marvin van Aalst',
    'author_email': 'marvin.vanaalst@gmail.com',
    'maintainer': 'Marvin van Aalst',
    'maintainer_email': 'marvin.vanaalst@gmail.com',
    'url': 'https://gitlab.com/qtb-hhu/modelbase-software',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
