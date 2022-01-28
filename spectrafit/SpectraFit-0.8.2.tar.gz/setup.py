# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spectrafit', 'spectrafit.test']

package_data = \
{'': ['*'], 'spectrafit.test': ['export/*', 'import/*', 'scripts/*']}

install_requires = \
['PyYAML>=6.0.0,<7.0.0',
 'corner>=2.2.1,<3.0.0',
 'dill>=0.3.4,<0.4.0',
 'emcee>=3.1.1,<4.0.0',
 'lmfit>=1.0.2,<2.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numdifftools>=0.9.40,<0.10.0',
 'numpy>=1.21.1,<2.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.3.0,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'statsmodels>=0.13.1,<0.14.0',
 'tabulate>=0.8.9,<0.9.0',
 'toml>=0.10.2,<0.11.0',
 'tqdm>=4.62.3,<5.0.0']

extras_require = \
{'all': ['ray[tune]>=1.9.1,<2.0.0',
         'tune>=0.0.9,<0.0.10',
         'hyperopt>=0.2.7,<0.3.0',
         'optuna>=2.10.0,<3.0.0'],
 'hyperopt': ['hyperopt>=0.2.7,<0.3.0'],
 'optuna': ['optuna>=2.10.0,<3.0.0'],
 'ray': ['ray[tune]>=1.9.1,<2.0.0'],
 'tune': ['tune>=0.0.9,<0.0.10']}

entry_points = \
{'console_scripts': ['spectrafit = spectrafit.spectrafit:command_line_runner']}

setup_kwargs = {
    'name': 'spectrafit',
    'version': '0.8.2',
    'description': 'Fast fitting of 2D-Spectra with established routines',
    'long_description': '[![CI - Python Package](https://github.com/Anselmoo/spectrafit/actions/workflows/python-ci.yml/badge.svg?branch=main)](https://github.com/Anselmoo/spectrafit/actions/workflows/python-ci.yml)\n[![codecov](https://codecov.io/gh/Anselmoo/spectrafit/branch/main/graph/badge.svg?token=pNIMKwWsO2)](https://codecov.io/gh/Anselmoo/spectrafit)\n[![PyPI](https://img.shields.io/pypi/v/spectrafit?logo=PyPi&logoColor=yellow)](https://pypi.org/project/spectrafit/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/spectrafit?color=gree&logo=Python&logoColor=yellow)](https://pypi.org/project/spectrafit/)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Anselmoo/spectrafit/main.svg)](https://results.pre-commit.ci/latest/github/Anselmoo/spectrafit/main)\n\n<p align="center">\n<img src="https://github.com/Anselmoo/spectrafit/blob/c5f7ee05e5610fb8ef4e237a88f62977b6f832e5/docs/images/spectrafit_synopsis.png?raw=true">\n</p>\n\n# SpectraFit\n\n`SpectraFit` is a command line tool for quick data fitting based on the regular\nexpression of distribution and linear functions. Furthermore, it can be also\nused as a module in existing python code. A previous version of `SpectraFit` was\nused for the following publication:\n\n- [Measurement of the Ligand Field Spectra of Ferrous and Ferric Iron Chlorides Using 2p3d RIXS](https://pubs.acs.org/doi/abs/10.1021/acs.inorgchem.7b00940)\n\nNow, it is completely rewritten and is more flexible. It is supporting all\ncommon ASCII-data formats and it run on `Linux`, `Windows`, and `MacOS`.\n\n## Scope\n\n- Fitting of 2D data\n- Using established and advanced solver methods\n- Extensibility of the fitting function\n- Guarantee traceability of the fitting results\n- Saving all results in a _SQL-like-format_ (`CSV`) for publications\n- Saving all results in a _NoSQL-like-format_ (`JSON`) for project management\n- Having an API interface for Graph-databases\n\n## Installation\n\nvia pip:\n\n```terminal\npip install spectrafit\n\n# Upgrade\n\npip install spectrafit --upgrade\n```\n\n## Usage\n\n`SpectraFit` needs as command line tool only two things:\n\n1. The reference data, which should be fitted.\n2. The input file, which contains the initial model.\n\nAs model files [json](https://en.wikipedia.org/wiki/JSON),\n[toml](https://en.wikipedia.org/wiki/TOML), and\n[yaml](https://en.wikipedia.org/wiki/YAML) are supported. By making use of the\npython `**kwargs` feature, the input file can call most of the following\nfunctions of [LMFIT](https://lmfit.github.io/lmfit-py/index.html). LMFIT is the\nworkhorse for the fit optimization, which is macro wrapper based on:\n\n1. [NumPy](https://www.numpy.org/)\n2. [SciPy](https://www.scipy.org/)\n3. [uncertainties](https://pythonhosted.org/uncertainties/)\n\nIn case of `SpectraFit`, we have further extend the package by:\n\n1. [Pandas](https://pandas.pydata.org/)\n2. [statsmodels](https://www.statsmodels.org/stable/index.html)\n3. [numdifftools](https://github.com/pbrod/numdifftools)\n4. [Matplotlib](https://matplotlib.org/) in combination with\n   [Seaborn](https://seaborn.pydata.org/)\n\n```terminal\nspectrafit data_file.txt -i input_file.json\n```\n\n```terminal\nusage: spectrafit [-h] [-o OUTFILE] [-i INPUT] [-ov] [-e0 ENERGY_START]\n                  [-e1 ENERGY_STOP] [-s SMOOTH] [-sh SHIFT] [-c COLUMN COLUMN]\n                  [-sep {       ,,,;,:,|, ,s+}] [-dec {.,,}] [-hd HEADER]\n                  [-g {0,1,2}] [-auto] [-np] [-v] [-vb {0,1,2}]\n                  infile\n\nFast Fitting Program for ascii txt files.\n\npositional arguments:\n  infile                Filename of the spectra data\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUTFILE, --outfile OUTFILE\n                        Filename for the export, default to set to\n                        \'spectrafit_results\'.\n  -i INPUT, --input INPUT\n                        Filename for the input parameter, default to set to\n                        \'fitting_input.toml\'.Supported fileformats are:\n                        \'*.json\', \'*.yml\', \'*.yaml\', and \'*.toml\'\n  -ov, --oversampling   Oversampling the spectra by using factor of 5;\n                        default to False.\n  -e0 ENERGY_START, --energy_start ENERGY_START\n                        Starting energy in eV; default to start of energy.\n  -e1 ENERGY_STOP, --energy_stop ENERGY_STOP\n                        Ending energy in eV; default to end of energy.\n  -s SMOOTH, --smooth SMOOTH\n                        Number of smooth points for lmfit; default to 0.\n  -sh SHIFT, --shift SHIFT\n                        Constant applied energy shift; default to 0.0.\n  -c COLUMN COLUMN, --column COLUMN COLUMN\n                        Selected columns for the energy- and intensity-values;\n                        default to \'0\' for energy (x-axis) and \'1\' for intensity\n                        (y-axis). In case of working with header, the column\n                        should be set to the column names as \'str\'; default\n                        to 0 and 1.\n  -sep { ,,,;,:,|, ,s+}, --separator { ,,,;,:,|, ,s+}\n                        Redefine the type of separator; default to \' \'.\n  -dec {.,,}, --decimal {.,,}\n                        Type of decimal separator; default to \'.\'.\n  -hd HEADER, --header HEADER\n                        Selected the header for the dataframe; default to None.\n  -g {0,1,2}, --global {0,1,2}\n                        Perform a global fit over the complete dataframe. The\n                        options are \'0\' for classic fit (default). The\n                        option \'1\' for global fitting with auto-definition\n                        of the peaks depending on the column size and \'2\'\n                        for self-defined global fitting routines.\n  -auto, --autopeak     Auto detection of peaks in the spectra based on `SciPy`.\n                        The position, height, and width are used as estimation\n                        for the `Gaussian` models.The default option is \'False\'\n                        for  manual peak definition.\n  -np, --noplot         No plotting the spectra and the fit of `SpectraFit`.\n  -v, --version         Display the current version of `SpectraFit`.\n  -vb {0,1,2}, --verbose {0,1,2}\n                        Display the initial configuration parameters and fit\n                        results, as a table \'1\', as a dictionary \'2\', or not in\n                        the terminal \'0\'. The default option is set to 1 for\n                        table `printout`.\n```\n\n## Documentation\n\nPlease see the [extended documentation](https://anselmoo.github.io/spectrafit/)\nfor the full usage of `SpectraFit`.\n',
    'author': 'Anselm Hahn',
    'author_email': 'Anselm.Hahn@gmail.com',
    'maintainer': 'Anselm Hahn',
    'maintainer_email': 'Anselm.Hahn@gmail.com',
    'url': 'https://pypi.org/project/spectrafit/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
