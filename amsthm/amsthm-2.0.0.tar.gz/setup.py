# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['amsthm']

package_data = \
{'': ['*']}

install_requires = \
['panflute>=2.1.3']

extras_require = \
{'docs': ['sphinx>=3.3,<4.0', 'sphinx-bootstrap-theme', 'sphinxcontrib-apidoc'],
 'extras': ['coloredlogs>=14,<16'],
 'tests': ['coverage', 'coveralls', 'pytest', 'pytest-parallel>=0.1.1,<0.2.0']}

entry_points = \
{'console_scripts': ['amsthm = amsthm:main']}

setup_kwargs = {
    'name': 'amsthm',
    'version': '2.0.0',
    'description': 'amsthm—provide a syntax to use amsthm environments in pandoc, with output in LaTeX and HTML',
    'long_description': '===========================================================================================\namsthm—provide a syntax to use amsthm environments in pandoc, with output in LaTeX and HTML\n===========================================================================================\n\n:Date:   January 25, 2022\n\n.. contents::\n   :depth: 3\n..\n\n|Documentation Status| |image1|\n\n|GitHub Actions| |Coverage Status| |image2| |Codacy Code Quality Status| |Scrutinizer Status| |CodeClimate Quality Status|\n\n|Supported versions| |Supported implementations| |PyPI Wheel| |PyPI Package latest release| |GitHub Releases| |Development Status| |Downloads| |Commits since latest release| |License|\n\n|Conda Recipe| |Conda Downloads| |Conda Version| |Conda Platforms|\n\nIntroduction\n============\n\namsthm provide a syntax to use amsthm environments in pandoc, with output in LaTeX and HTML.\n\nUsage\n=====\n\nFrom ``makefile``:\n\n.. code:: makefile\n\n   tests/model-target.md: tests/model-source.md\n       pandoc -F amsthm $< -o $@\n   tests/model-latex.tex: tests/model-source.md\n       pandoc -F amsthm $< -o $@ --top-level-division=chapter --toc -N\n   tests/model-latex.pdf: tests/model-source.md\n       pandoc -F amsthm $< -o $@ --top-level-division=chapter --toc -N\n   tests/model-html.html: tests/model-source.md\n       pandoc -F amsthm $< -o $@ --toc -N -s\n\nSyntax\n======\n\nSee ``tests/model-source.md`` (or next page in documentation site) for an example.\n\nTips\n====\n\n-  Use ``-N``, ``--number-sections`` to enable numbering in pandoc. This is mandatory for LaTeX output.\n-  To match LaTeX and non-LaTeX output numbering scheme, match these 2 settings manually\n\n   -  LaTeX output: pandoc’s cli flag ``--top-level-division=[section|chapter|part]`` and the use of ``parent_counter`` in pandoc-amsthm\n   -  non-LaTeX output: ``counter_depth`` in pandoc-amsthm\n\nSupported pandoc versions\n=========================\n\npandoc versioning semantics is `MAJOR.MAJOR.MINOR.PATCH <https://pvp.haskell.org>`__ and panflute’s is MAJOR.MINOR.PATCH. Below we shows matching versions of pandoc that panflute supports, in descending order. Only major version is shown as long as the minor versions doesn’t matter.\n\n.. table:: Version Matching [1]_\n\n   +---------------+------------------+---------------------------+-------------------------------+\n   | pandoc-amsthm | panflute version | supported pandoc versions | supported pandoc API versions |\n   +===============+==================+===========================+===============================+\n   | 2.0.0         | 2.1.3            | 2.14.0.3–2.17.x           | 1.22–1.22.1                   |\n   +---------------+------------------+---------------------------+-------------------------------+\n\n.. [1]\n   For pandoc API verion, check https://hackage.haskell.org/package/pandoc for pandoc-types, which is the same thing.\n\n.. |Documentation Status| image:: https://readthedocs.org/projects/pandoc-amsthm/badge/?version=latest\n   :target: https://pandoc-amsthm.readthedocs.io/en/latest/?badge=latest&style=plastic\n.. |image1| image:: https://github.com/ickc/pandoc-amsthm/workflows/GitHub%20Pages/badge.svg\n   :target: https://ickc.github.io/pandoc-amsthm\n.. |GitHub Actions| image:: https://github.com/ickc/pandoc-amsthm/workflows/Python%20package/badge.svg\n.. |Coverage Status| image:: https://codecov.io/gh/ickc/pandoc-amsthm/branch/master/graphs/badge.svg?branch=master\n   :target: https://codecov.io/github/ickc/pandoc-amsthm\n.. |image2| image:: https://coveralls.io/repos/ickc/pandoc-amsthm/badge.svg?branch=master&service=github\n   :target: https://coveralls.io/r/ickc/pandoc-amsthm\n.. |Codacy Code Quality Status| image:: https://img.shields.io/codacy/grade/078ebc537c5747f68c1d4ad3d3594bbf.svg\n   :target: https://www.codacy.com/app/ickc/pandoc-amsthm\n.. |Scrutinizer Status| image:: https://img.shields.io/scrutinizer/quality/g/ickc/pandoc-amsthm/master.svg\n   :target: https://scrutinizer-ci.com/g/ickc/pandoc-amsthm/\n.. |CodeClimate Quality Status| image:: https://codeclimate.com/github/ickc/pandoc-amsthm/badges/gpa.svg\n   :target: https://codeclimate.com/github/ickc/pandoc-amsthm\n.. |Supported versions| image:: https://img.shields.io/pypi/pyversions/amsthm.svg\n   :target: https://pypi.org/project/amsthm\n.. |Supported implementations| image:: https://img.shields.io/pypi/implementation/amsthm.svg\n   :target: https://pypi.org/project/amsthm\n.. |PyPI Wheel| image:: https://img.shields.io/pypi/wheel/amsthm.svg\n   :target: https://pypi.org/project/amsthm\n.. |PyPI Package latest release| image:: https://img.shields.io/pypi/v/amsthm.svg\n   :target: https://pypi.org/project/amsthm\n.. |GitHub Releases| image:: https://img.shields.io/github/tag/ickc/pandoc-amsthm.svg?label=github+release\n   :target: https://github.com/ickc/pandoc-amsthm/releases\n.. |Development Status| image:: https://img.shields.io/pypi/status/amsthm.svg\n   :target: https://pypi.python.org/pypi/amsthm/\n.. |Downloads| image:: https://img.shields.io/pypi/dm/amsthm.svg\n   :target: https://pypi.python.org/pypi/amsthm/\n.. |Commits since latest release| image:: https://img.shields.io/github/commits-since/ickc/pandoc-amsthm/v2.0.0.svg\n   :target: https://github.com/ickc/pandoc-amsthm/compare/v2.0.0...master\n.. |License| image:: https://img.shields.io/pypi/l/amsthm.svg\n.. |Conda Recipe| image:: https://img.shields.io/badge/recipe-amsthm-green.svg\n   :target: https://anaconda.org/conda-forge/amsthm\n.. |Conda Downloads| image:: https://img.shields.io/conda/dn/conda-forge/amsthm.svg\n   :target: https://anaconda.org/conda-forge/amsthm\n.. |Conda Version| image:: https://img.shields.io/conda/vn/conda-forge/amsthm.svg\n   :target: https://anaconda.org/conda-forge/amsthm\n.. |Conda Platforms| image:: https://img.shields.io/conda/pn/conda-forge/amsthm.svg\n   :target: https://anaconda.org/conda-forge/amsthm\n',
    'author': 'Kolen Cheung',
    'author_email': 'christian.kolen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ickc/amsthm',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
