# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pspipe', 'pspipe.tests', 'pspipe.tools']

package_data = \
{'': ['*'], 'pspipe': ['templates/*', 'templates/config/*']}

install_requires = \
['astropy>=3.2,<5.0',
 'matplotlib>=3.0,<4.0',
 'nenucal>=0.1.11',
 'ps-eor>=0.8',
 'python-casacore>=3.0,<4.0',
 'tables>=3.2,<4.0',
 'tabulate>=0.8',
 'toml>=0.10']

entry_points = \
{'console_scripts': ['psdb = pspipe.tools.psdb:main',
                     'pspipe = pspipe.tools.pspipe:main']}

setup_kwargs = {
    'name': 'pspipe',
    'version': '0.1.9',
    'description': 'Power spectra pipeline for Cosmic Dawn, Epoch of Reionization radio interferometric experiments',
    'long_description': 'Power Spectra Generation pipeline for CD/EoR experiments\n========================================================\n\npspipe is an analysis pipeline which aims to make generation of high precision power-spectra for Cosmic Dawn and Epoch of Reionization experiments as easy and reproducible as possible. pspipe is the default analysis pipeline of the [Lofar-EoR](http://www.lofar.org/astronomy/eor-ksp/epoch-reionization.html) and [NenuFAR](https://nenufar.obs-nancay.fr/en/homepage-en/) CD projects. It performs all tasks from calibrated data to final the power-spectra, including:\n\n- Post-calibration flagging (using [AOflagger](https://sourceforge.net/p/aoflagger/wiki/Home/) and [SSINS](https://arxiv.org/abs/1906.01093))\n- Visibility gridding (using [WSClean](https://sourceforge.net/p/wsclean/wiki/Home/))\n- Foregrounds modeling and removal (using [GPR](https://doi.org/10.1093/mnras/sty1207), [GMCA](https://arxiv.org/abs/1209.4769), polynomial fitting)\n- Optimal power-spectra generation (using [ps_eor](https://gitlab.com/flomertens/ps_eor))\n\nThanks to its multi-nodes concurrent processing, pspipe is also very fast at crunching hundreds of hour of calibrated data.\n\nInstallation\n------------\n\npspipe can be installed via pip:\n\n    $ pip install pspipe\n\nand requires Python 3.7.0 or higher. For certain tasks, you will also need [DPPP](https://github.com/lofar-astron/DP3/tree/master/DPPP) and [WSClean](https://sourceforge.net/p/wsclean/wiki/Home/)\n\nDocumentation\n--------------\n\nPlease check the [wiki page](https://gitlab.com/flomertens/pspipe/-/wikis/home).\n',
    'author': '"Florent Mertens"',
    'author_email': '"florent.mertens@gmail.com"',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/flomertens/pspipe/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
