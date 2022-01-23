# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['eko',
 'eko.anomalous_dimensions',
 'eko.evolution_operator',
 'eko.kernels',
 'eko.matching_conditions',
 'ekomark',
 'ekomark.benchmark',
 'ekomark.benchmark.external',
 'ekomark.data',
 'ekomark.navigator']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'lz4>=3.1.10,<4.0.0',
 'numba>=0.55.0,<0.56.0',
 'numpy>=1.21.0,<2.0.0',
 'scipy>=1.7.3,<2.0.0']

extras_require = \
{'docs': ['Sphinx>=4.3.2,<5.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0',
          'sphinxcontrib-bibtex>=2.4.1,<3.0.0'],
 'mark': ['banana-hep>=0.5.9,<0.6.0',
          'sqlalchemy>=1.4.21,<2.0.0',
          'pandas>=1.3.0,<2.0.0',
          'matplotlib>=3.5.1,<4.0.0']}

entry_points = \
{'console_scripts': ['ekonav = ekomark.navigator:launch_navigator']}

setup_kwargs = {
    'name': 'eko',
    'version': '0.8.4',
    'description': 'Evolution Kernel Operator',
    'long_description': '<p align="center">\n  <a href="https://n3pdf.github.io/eko/"><img alt="EKO" src="https://raw.githubusercontent.com/N3PDF/eko/master/doc/source/img/Logo.png" width=300></a>\n</p>\n<p align="center">\n  <a href="https://github.com/N3PDF/eko/actions?query=workflow%3A%22eko%22"><img alt="Tests" src="https://github.com/N3PDF/eko/workflows/eko/badge.svg" /></a>\n  <a href="https://eko.readthedocs.io/en/latest/?badge=latest"><img alt="Docs" src="https://readthedocs.org/projects/eko/badge/?version=latest"></a>\n  <a href="https://codecov.io/gh/N3PDF/eko"><img src="https://codecov.io/gh/N3PDF/eko/branch/master/graph/badge.svg" /></a>\n  <a href="https://www.codefactor.io/repository/github/n3pdf/eko"><img src="https://www.codefactor.io/repository/github/n3pdf/eko/badge" alt="CodeFactor" /></a>\n</p>\n\nEKO is a Python module to solve the DGLAP equations in terms of Evolution Kernel Operators in x-space.\n\n## Installation\nEKO is available via PyPI: <a href="https://pypi.org/project/eko/"><img alt="PyPI" src="https://img.shields.io/pypi/v/eko"/></a> - so you can simply run\n```bash\npip install eko\n```\n\n### Development\n\nIf you want to install from source you can run\n```bash\ngit clone git@github.com:N3PDF/eko.git\ncd eko\npoetry install\n```\n\nTo setup `poetry`, and other tools, see [Contribution\nGuidlines](https://github.com/N3PDF/eko/blob/master/.github/CONTRIBUTING.md).\n\n## Documentation\n- The documentation is available here: <a href="https://eko.readthedocs.io/en/latest/?badge=latest"><img alt="Docs" src="https://readthedocs.org/projects/eko/badge/?version=latest"></a>\n- To build the documentation from source install [graphviz](https://www.graphviz.org/) and run in addition to the installation commands\n```bash\npip install -r dev_requirements.txt\ncd doc\nmake html\n```\n\n## Citation policy\nPlease cite our DOI when using our code: <a href="https://doi.org/10.5281/zenodo.3874237"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.3874237.svg" alt="DOI"/></a>\n\n## Contributing\n- Your feedback is welcome! If you want to report a (possible) bug or want to ask for a new feature, please raise an issue: <a href="https://img.shields.io/github/issues/N3PDF/eko"><img alt="GitHub issues" src="https://img.shields.io/github/issues/N3PDF/eko"/></a>\n- Please follow our [Code of Conduct](https://github.com/N3PDF/eko/blob/master/.github/CODE_OF_CONDUCT.md) and read the\n  [Contribution Guidlines](https://github.com/N3PDF/eko/blob/master/.github/CONTRIBUTING.md)\n',
    'author': 'A. Candido',
    'author_email': 'alessandro.candido@mi.infn.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/N3PDF/eko',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
