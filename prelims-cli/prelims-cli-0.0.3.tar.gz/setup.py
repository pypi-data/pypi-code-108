# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prelims_cli', 'prelims_cli.config', 'prelims_cli.ja']

package_data = \
{'': ['*']}

install_requires = \
['hydra-core>=1.1.1,<2.0.0',
 'numpy>=1.22.1,<2.0.0',
 'prelims>=0.0.6,<0.0.7',
 'scipy>=1.7.3,<2.0.0',
 'taskipy>=1.9.0,<2.0.0']

extras_require = \
{'ja': ['SudachiPy>=0.6.2,<0.7.0', 'SudachiDict-full>=20211220,<20211221']}

entry_points = \
{'console_scripts': ['prelims-cli = prelims_cli.cli:main']}

setup_kwargs = {
    'name': 'prelims-cli',
    'version': '0.0.3',
    'description': 'prelims CLI - Front matter post-processor CLI',
    'long_description': '# prelims-cli\n\nCLI for [prelims](https://github.com/takuti/prelims).\n\n## Install\n\nRun:\n\n```sh\npip install prelims-cli\n```\n\nIf you need Japanese tokenization, run:\n\n```sh\npip install prelims-cli[ja]\n```\n\n## Usage\n\nAssuming the following folder directory:\n\n```sh\n- content\n|  ├── post\n|  └── blog\n└─ scripts\n   └ config\n     └ myconfig.yaml\n```\n\nwhere, post and blog are pages, and scripts is the place to put scripts.\n\nHere is the example of configuration:\n\n```myconfig.yaml\nhandlers:\n  - target_path: "content/blog"\n    ignore_files:\n      - _index.md\n    processors:\n      - type: recommender\n        permalink_base: "/blog"\n        tfidf_options:\n          stop_words: english\n          max_df: 0.95\n          min_df: 2\n        tokenizer: null\n  - target_path: "content/post"\n    ignore_files:\n      - _index.md\n    processors:\n      - type: recommender\n        permalink_base: "/post"\n        tfidf_options:\n          max_df: 0.95\n          min_df: 2\n        tokenizer:\n          lang: ja\n          type: sudachi\n          mode: C\n          dict: full\n```\n\n```sh\n$ prelims-cli --config-dir ./scripts/config --config-name myconfig hydra.run.dir=. hydra.output_subdir=null hydra/job_logging=disabled hydra/hydra_logging=disabled\ntarget: /user/chezo/src/chezo.uno/content/blog\ntarget: /users/chezo/src/chezo.uno/content/post\n```\n\nThen your articles\' front matter were updated.\n',
    'author': 'Aki Ariga',
    'author_email': 'chezou@gmail.com',
    'maintainer': 'Aki Ariga',
    'maintainer_email': 'chezou@gmail.com',
    'url': 'https://github.com/chezou/prelims-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
