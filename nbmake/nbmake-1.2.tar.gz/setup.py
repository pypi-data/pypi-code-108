# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nbmake']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.7.3,<3.0.0',
 'ipykernel>=5.4.0',
 'nbclient>=0.5.5,<0.6.0',
 'nbformat>=5.0.8,<6.0.0',
 'pydantic>=1.7.2,<2.0.0',
 'pytest>=6.1.0,<7.0.0']

entry_points = \
{'pytest11': ['nbmake = nbmake.pytest_plugin']}

setup_kwargs = {
    'name': 'nbmake',
    'version': '1.2',
    'description': 'Pytest plugin for testing notebooks',
    'long_description': '# nbmake\n[![codecov](https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO)](https://codecov.io/gh/treebeardtech/nbmake)\n[![PyPI versions](https://img.shields.io/pypi/pyversions/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake)\n[![PyPI versions](https://img.shields.io/pypi/v/nbmake?logo=python&logoColor=white)](https://pypi.org/project/nbmake)\n[![PyPI Downloads](https://img.shields.io/pypi/dm/nbmake)](https://pypi.org/project/nbmake)\n[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-908a85?logo=gitpod)](https://gitpod.io/#https://github.com/treebeardtech/nbmake)\n\n**What?** Pytest plugin for testing and releasing notebook documentation\n\n**Why?** To raise the quality of scientific material through better automation\n\n**Who is this for?** Research/Machine Learning Software Engineers who maintain packages/teaching materials with documentation written in notebooks.\n\n## Functionality\n\n1. Executes notebooks using pytest and nbclient, allowing parallel notebook testing\n2. Optionally writes back to the repo, allowing faster building of [nbsphinx](https://github.com/spatialaudio/nbsphinx) or [jupyter book](https://github.com/executablebooks/jupyter-book) docs\n\n## Quick Start\n\n```\npip install pytest nbmake\npytest --nbmake **/*ipynb\n```\n\n## Configure Cell Timeouts\n\nYou can configure the cell timeout with the following pytest flag:\n\n```sh\npytest --nbmake --nbmake-timeout=3000 # allows each cell 3000 seconds to finish\n```\n\n## Allow Errors For a Whole Notebook\n\nThis configuration must be placed in the notebook\'s **top-level metadata** (not cell-level metadata).\n\nYour notebook should look like this:\n\n```json\n{\n  "cells": [ ... ],\n  "metadata": {\n    "kernelspec": { ... },\n    "execution": {\n      "allow_errors": true,\n      "timeout": 300\n    }\n  }\n}\n```\n\n## Allow a Cell to Throw an Exception\n\nA cell with the following metadata can throw an exception without failing the test:\n\n```json\n{\n  "language": "python",\n  "custom": {\n    "metadata": {\n      "tags": [\n        "raises-exception"\n      ]\n    }\n  }\n}\n```\n\n## Ignore a Code Cell\n\nA cell with the following metadata will not be executed by nbmake\n\n```json\n{\n  "language": "python",\n  "custom": {\n    "metadata": {\n      "tags": [\n        "skip-execution"\n      ]\n    }\n  }\n}\n```\n\n## Override Notebook Kernels when Testing\n\nRegardless of the kernel configured in the notebook JSON, you can force nbmake to use a specific kernel when testing:\n\n```\npytest --nbmake --nbmake-kernel=mycustomkernel\n```\n\n## Add Missing Jupyter Kernel to Your CI Environment\n\nIf you are not using the flag above and are using a kernel name other than the default ‘python3’, you will see an error message when executing your notebooks in a fresh CI environment: `Error - No such kernel: \'mycustomkernel\'`\n\nUse ipykernel to install the custom kernel:\n\n```sh\npython -m ipykernel install --user --name mycustomkernel\n```\n\nIf you are using another language such as c++ in your notebooks, you may have a different process for installing your kernel.\n\n## Parallelisation\n\nParallelisation with xdist is experimental upon initial release, but you can try it out:\n```\npip install pytest-xdist\n\npytest --nbmake -n=auto\n```\n\nIt is also possible to parallelise at a CI-level using strategies, see [example](https://github.com/LabForComputationalVision/plenoptic/blob/master/.github/workflows/treebeard.yml)\n\n### Build Jupyter Books Faster\n\nUsing xdist and the `--overwrite` flag let you build a large jupyter book repo faster:\n\n```\npytest --nbmake --overwrite -n=auto examples\njb build examples\n```\n\n## Advice on Usage\n\nnbmake is best used in a scenario where you use the ipynb files only for development. Consumption of notebooks is primarily done via a docs site, built through jupyter book, nbsphinx, or some other means. If using one of these tools, you are able to write assertion code in cells which will be [hidden from readers](https://jupyterbook.org/interactive/hiding.html).\n\n### Pre-commit\n\nTreating notebooks like source files lets you keep your repo minimal. Some tools, such as plotly may drop several megabytes of javascript in your output cells, as a result, stripping out notebooks on pre-commit is advisable:\n\n```\n# .pre-commit-config.yaml\nrepos:\n  - repo: https://github.com/kynan/nbstripout\n    rev: master\n    hooks:\n      - id: nbstripout\n```\n\nSee https://pre-commit.com/ for more...\n\n## Disable Nbmake\n\nImplicitly:\n```\npytest\n```\n\nExplicitly:\n```\npytest -p no:nbmake\n```\n\n## See Also:\n\n* A more in-depth [intro to nbmake](https://semaphoreci.com/blog/test-jupyter-notebooks-with-pytest-and-nbmake) running on Semaphore CI\n* [nbmake action](https://github.com/treebeardtech/treebeard)\n* [pytest](https://pytest.org/)\n* [jupyter book](https://github.com/executablebooks/jupyter-book)\n* [jupyter cache](https://github.com/executablebooks/jupyter-cache)\n* [MyST-NB](https://github.com/executablebooks/MyST-NB)\n',
    'author': 'alex-treebeard',
    'author_email': 'alex@treebeard.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/treebeardtech/nbmake',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
