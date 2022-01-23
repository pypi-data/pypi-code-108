# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['banana',
 'banana.benchmark',
 'banana.benchmark.external',
 'banana.data',
 'banana.data.genpdf',
 'banana.navigator']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'SQLAlchemy>=1.4.29,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'eko>=0.8.2,<0.9.0',
 'ipython>=7.30.1,<8.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'rich>=10.16.1,<11.0.0']

extras_require = \
{'docs': ['Sphinx>=4.3.2,<5.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0',
          'sphinxcontrib-bibtex>=2.4.1,<3.0.0']}

entry_points = \
{'console_scripts': ['genpdf = banana.data.genpdf.cli:cli']}

setup_kwargs = {
    'name': 'banana-hep',
    'version': '0.5.9',
    'description': 'Benchmark QCD physics',
    'long_description': '<p align="center">\n  <a href="https://n3pdf.github.io/banana/"><img alt="Banana" src="https://raw.githubusercontent.com/N3PDF/banana/main/docs/_assets/logo.png" width=700></a>\n</p>\n\n<p align="center">\n  <a href="https://github.com/N3PDF/banana/actions?query=workflow%3A%22unit+tests%22">\n    <img alt="Tests" src="https://github.com/N3PDF/banana/workflows/unit%20tests/badge.svg">\n  </a>\n  <a href=\'https://banana-hep.readthedocs.io/en/latest/?badge=latest\'><img src=\'https://readthedocs.org/projects/banana-hep/badge/?version=latest\' alt=\'Documentation Status\' /></a>\n  <a href="https://pypi.org/project/banana-hep/"><img alt="PyPI" src="https://img.shields.io/pypi/v/banana-hep"/></a>\n  <a href="https://doi.org/10.5281/zenodo.4247164"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.4247164.svg" alt="DOI"></a>\n  <a href="https://codecov.io/gh/N3PDF/banana">\n    <img src="https://codecov.io/gh/N3PDF/banana/branch/main/graph/badge.svg?token=L9XIAXV77R"/>\n  </a>\n  <a href="https://www.codefactor.io/repository/github/n3pdf/banana">\n    <img src="https://www.codefactor.io/repository/github/n3pdf/banana/badge?s=1f7766473570c0d6432d5a2d216498b09a50c2b5" alt="CodeFactor" />\n  </a>\n</p>\n\n# banana: Benchmarking AgaiNst Apfel aNd Anything\n\nThis is the base package of ekomark and yadmark\n',
    'author': 'Andrea Barontini',
    'author_email': 'andrea.barontini@mi.infn.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/N3PDF/banana',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
