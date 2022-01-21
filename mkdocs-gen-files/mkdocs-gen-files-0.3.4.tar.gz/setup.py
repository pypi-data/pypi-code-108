# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkdocs_gen_files']

package_data = \
{'': ['*']}

install_requires = \
['mkdocs>=1.0.3,<2.0.0']

entry_points = \
{'mkdocs.plugins': ['gen-files = mkdocs_gen_files.plugin:GenFilesPlugin']}

setup_kwargs = {
    'name': 'mkdocs-gen-files',
    'version': '0.3.4',
    'description': 'MkDocs plugin to programmatically generate documentation pages during the build',
    'long_description': '# mkdocs-gen-files\n\n**[Plugin][] for [MkDocs][] to programmatically generate documentation pages during the build**\n\n[![PyPI](https://img.shields.io/pypi/v/mkdocs-gen-files)](https://pypi.org/project/mkdocs-gen-files/)\n[![GitHub](https://img.shields.io/github/license/oprypin/mkdocs-gen-files)](https://github.com/oprypin/mkdocs-gen-files/blob/master/LICENSE.md)\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/oprypin/mkdocs-gen-files/CI)](https://github.com/oprypin/mkdocs-gen-files/actions?query=event%3Apush+branch%3Amaster)\n\n```shell\npip install mkdocs-gen-files\n```\n\n**Continue to the [documentation site][].**\n\n[mkdocs]: https://www.mkdocs.org/\n[plugin]: https://www.mkdocs.org/user-guide/plugins/\n[documentation site]: https://oprypin.github.io/mkdocs-gen-files\n\n## Usage\n\nActivate the plugin in **mkdocs.yml** (`scripts` is a required list of Python scripts to execute):\n\n```yaml\nplugins:\n  - search\n  - gen-files:\n      scripts:\n        - gen_pages.py  # or any other name or path\n```\n\nThen create such a script **gen_pages.py** (this is relative to the root, *not* to the *docs* directory).\n\n```python\nimport mkdocs_gen_files\n\nwith mkdocs_gen_files.open("foo.md", "w") as f:\n    print("Hello, world!", file=f)\n```\n\nThis added a programmatically generated page to our site. That is, the document doesn\'t actually appear in our source files, it only *virtually* becomes part of the site to be built by MkDocs.\n\n**Continue to the [documentation site][].**\n',
    'author': 'Oleh Prypin',
    'author_email': 'oleh@pryp.in',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/oprypin/mkdocs-gen-files',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
