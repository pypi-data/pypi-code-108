# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['yadbox',
 'yadbox.runcards',
 'yadism',
 'yadism.coefficient_functions',
 'yadism.coefficient_functions.fonll',
 'yadism.coefficient_functions.heavy',
 'yadism.coefficient_functions.intrinsic',
 'yadism.coefficient_functions.light',
 'yadism.coefficient_functions.light.nlo',
 'yadism.coefficient_functions.light.nnlo',
 'yadism.coefficient_functions.special',
 'yadism.coefficient_functions.splitting_functions',
 'yadism.coefficient_functions.splitting_functions.nlo',
 'yadism.esf',
 'yadism.input',
 'yadmark',
 'yadmark.benchmark',
 'yadmark.benchmark.external',
 'yadmark.data',
 'yadmark.navigator']

package_data = \
{'': ['*']}

install_requires = \
['LeProHQ>=0.2.0,<0.3.0',
 'eko>=0.8.2,<0.9.0',
 'numba>=0.55.0,<0.56.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'rich>=10.6.0,<11.0.0',
 'scipy>=1.7.0,<2.0.0']

extras_require = \
{'docs': ['Sphinx>=4.1.1,<5.0.0',
          'sphinx-rtd-theme>=0.5.2,<0.6.0',
          'recommonmark>=0.7.1,<0.8.0',
          'sphinxcontrib-bibtex>=2.3.0,<3.0.0',
          'sphinxcontrib-details-directive>=0.1.0,<0.2.0',
          'nbsphinx>=0.8.6,<0.9.0'],
 'mark': ['banana-hep>=0.4.0,<0.5.0',
          'sqlalchemy>=1.4.21,<2.0.0',
          'a3b2bbc3ced97675ac3a71df45f55ba>=6.4.0,<7.0.0'],
 'pineappl': ['pineappl==0.5.0_beta.6']}

entry_points = \
{'console_scripts': ['yanav = yadmark.navigator:launch_navigator']}

setup_kwargs = {
    'name': 'yadism',
    'version': '0.10.4',
    'description': 'Yet Another Deep-Inelastic Scattering Module',
    'long_description': '<p align="center">\n  <a href="https://n3pdf.github.io/yadism/"><img alt="Yadism" src="https://raw.githubusercontent.com/N3PDF/yadism/master/docs/_assets/logo/logo.png" width=600></a>\n</p>\n\n<p align="center">\n  <a href="https://github.com/N3PDF/yadism/actions?query=workflow%3A%22yadism%22"><img alt="Tests" src="https://github.com/N3PDF/yadism/workflows/yadism/badge.svg"></a>\n  <a href=\'https://yadism.readthedocs.io/en/latest/?badge=latest\'><img src=\'https://readthedocs.org/projects/yadism/badge/?version=latest\' alt=\'Documentation Status\' /></a>\n  <a href="https://pypi.org/project/yadism/"><img alt="PyPI" src="https://img.shields.io/pypi/v/yadism"/></a>\n  <a href="https://codecov.io/gh/N3PDF/yadism"><img src="https://codecov.io/gh/N3PDF/yadism/branch/master/graph/badge.svg?token=qgCFyUQ6oG" /></a>\n  <a href="https://www.codefactor.io/repository/github/n3pdf/yadism"><img src="https://www.codefactor.io/repository/github/n3pdf/yadism/badge?s=e5a00668b58574b5b056e1aca01c7b25d2c203f8" alt="CodeFactor" /></a>\n  <a href="https://zenodo.org/badge/latestdoi/219968694"><img src="https://zenodo.org/badge/219968694.svg" alt="DOI"></a>\n</p>\n\n<!--Future Badges\n/github/workflow/status/N3PDF/dis/yadism\n\nuse the ones provided by shields.io:\n- example: https://img.shields.io/github/workflow/status/N3PDF/yadism\n\nnote: in order to make shields.io the repo must be public (or accessible to it in some way)\n\noptional:\n- Release-date (github):\n  - /github/release-date/:user/:repo\n- Downloads:\n  - github: /github/downloads/:user/:repo/total\n  - pypi: /pypi/:period/:packageName\n- License:\n  - pypi-license: /pypi/l/:packageName\n  - github-license: /github/license/:user/:repo\n- Activity:\n  - open-issues (github): /github/issues/:user/:repo\n  - open-pull-requests (github): /github/issues-pr/:user/:repo\n- Code size:\n  - github: /github/languages/code-size/:user/:repo\n-->\n\n## Scope of the project\n\nProvide all necessary tools to compute the DIS structure functions and related objects. This project is linked closely to [EKO](https://github.com/N3PDF/eko).\n\n## Installation\n\nAs a user please use [the released version on PyPI](https://pypi.org/project/yadism/),\nthrough your python package manager, e.g. with `pip`:\n\n```sh\npip install yadism\n```\n\n### Dev\n\nFor development just use the install script and poetry (provided by install\nscript):\n\n```sh\npython install.py\npoetry install\n```\n\n## Development\n\nMembers of the development team should always follow the [contribution\nguidelines](.github/contributing.md), to have a uniform strategy in code\ndevelopment and improve collaboration.\n\n## Contributing or contacting the authors\n\nFor any kind of interaction consider before to read [external contribution\nguidelines](.github/contributing.md#external-contributions), otherwise just send\nan email to the authors:\n\n- [Alessandro Candido](mailto:alessandro.candido@mi.infn.it)\n- [Felix Hekhorn](mailto:felix.hekhorn@mi.infn.it)\n- [Giacomo Magni](mailto:gmagni@nikhef.nl)\n',
    'author': 'Alessandro Candido',
    'author_email': 'alessandro.candido@mi.infn.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://n3pdf.github.io/yadism/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
