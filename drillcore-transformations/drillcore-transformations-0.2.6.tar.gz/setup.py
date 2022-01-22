# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drillcore_transformations']

package_data = \
{'': ['*']}

install_requires = \
['click', 'matplotlib', 'numpy', 'openpyxl', 'pandas', 'xlrd']

extras_require = \
{'coverage': ['coverage>=5.0,<6.0', 'coverage-badge'],
 'docs': ['sphinx',
          'sphinx-rtd-theme',
          'nbsphinx',
          'sphinx-gallery',
          'sphinx-autodoc-typehints'],
 'format-lint': ['sphinx',
                 'pylint',
                 'rstcheck',
                 'black[jupyter]',
                 'blacken-docs',
                 'blackdoc',
                 'isort'],
 'typecheck': ['mypy']}

entry_points = \
{'console_scripts': ['drillcore-transformations = '
                     'drillcore_transformations.cli:cli']}

setup_kwargs = {
    'name': 'drillcore-transformations',
    'version': '0.2.6',
    'description': 'Transform structural drillcore measurements.',
    'long_description': 'Drillcore Transformations\n=========================\n\n|Documentation Status| |PyPI Status| |CI Test| |Coverage|\n\nFeatures\n--------\n\n-  Transforms measurements from drillcores.\n-  Supports alpha, beta and gamma measurements.\n-  Supports .csv and .xlsx files.\n-  Supports adding the column names of your data files to a custom-built\n   config.ini file for each user.\n-  TODO: Convention support\n-  Currently supported convention explanation found in `Documentation\n   and Help <https://drillcore-transformations.readthedocs.io>`__\n-  **Documentation and Help**:\n   https://drillcore-transformations.readthedocs.io.\n\nRunning tests\n-------------\n\nTo run pytest in currently installed environment:\n\n.. code:: bash\n\n   poetry run pytest\n\nTo run full extensive test suite:\n\n.. code:: bash\n\n   poetry run invoke test\n\nFormatting and linting\n----------------------\n\nFormatting and linting is done with a single command. First formats,\nthen lints.\n\n.. code:: bash\n\n   poetry run invoke format-and-lint\n\nBuilding docs\n-------------\n\nDocs can be built locally to test that ``ReadTheDocs`` can also build\nthem:\n\n.. code:: bash\n\n   poetry run invoke docs\n\nInvoke usage\n------------\n\nTo list all available commands from ``tasks.py``:\n\n.. code:: bash\n\n   poetry run invoke --list\n\nDevelopment\n~~~~~~~~~~~\n\nDevelopment dependencies include:\n\n   -  invoke\n   -  nox\n   -  copier\n   -  pytest\n   -  coverage\n   -  sphinx\n\nBig thanks to all maintainers of the above packages!\n\nCredits\n-------\n\n-  PhD Jussi Mattila for tips, code snippets and sample materials.\n-  Authors of `Orientation uncertainty goes\n   bananas <https://tinyurl.com/tqr84ww>`__ for great article and\n   complementary excel-file.\n\nLicense\n~~~~~~~\n\nCopyright © 2020, Nikolas Ovaskainen.\n\n-----\n\n\n.. |Documentation Status| image:: https://readthedocs.org/projects/drillcore-transformations/badge/?version=latest\n   :target: https://drillcore-transformations.readthedocs.io/en/latest/?badge=latest\n.. |PyPI Status| image:: https://img.shields.io/pypi/v/drillcore-transformations.svg\n   :target: https://pypi.python.org/pypi/drillcore-transformations\n.. |CI Test| image:: https://github.com/nialov/drillcore-transformations/workflows/test-and-publish/badge.svg\n   :target: https://github.com/nialov/drillcore-transformations/actions/workflows/test-and-publish.yaml?query=branch%3Amaster\n.. |Coverage| image:: https://raw.githubusercontent.com/nialov/drillcore-transformations/master/docs_src/imgs/coverage.svg\n   :target: https://github.com/nialov/drillcore-transformations/blob/master/docs_src/imgs/coverage.svg\n',
    'author': 'nialov',
    'author_email': 'nikolasovaskainen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nialov/drillcore-transformations',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
