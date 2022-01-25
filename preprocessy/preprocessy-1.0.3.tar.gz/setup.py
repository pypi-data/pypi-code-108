# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['preprocessy',
 'preprocessy.data_splitting',
 'preprocessy.encoding',
 'preprocessy.feature_selection',
 'preprocessy.input',
 'preprocessy.missing_data',
 'preprocessy.outliers',
 'preprocessy.parse',
 'preprocessy.pipelines',
 'preprocessy.scaling',
 'preprocessy.utils']

package_data = \
{'': ['*'], 'preprocessy.scaling': ['math_funcs/*']}

install_requires = \
['alive-progress==2.1.0',
 'colorama==0.4.4',
 'pandas==1.3.4',
 'prettytable==2.1.0',
 'scikit-learn==0.24.2',
 'stringcase==1.2.0']

setup_kwargs = {
    'name': 'preprocessy',
    'version': '1.0.3',
    'description': 'Data Preprocessing library that provides customizable pipelines.',
    'long_description': "![preprocessy-logo](docs/_static/preprocessy_horizontal.png)\n\n[![Workflow](https://github.com/preprocessy/preprocessy/actions/workflows/workflow.yml/badge.svg)](https://github.com/preprocessy/preprocessy/actions/workflows/workflow.yml)\n[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-sucess.svg)](https://gitHub.com/preprocessy/preprocessy/graphs/commit-activity)\n[![Issues Open](https://img.shields.io/github/issues/preprocessy/preprocessy)](https://github.com/preprocessy/preprocessy/issues)\n[![Forks](https://img.shields.io/github/forks/preprocessy/preprocessy)](https://github.com/preprocessy/preprocessy/network/members)\n[![Stars](https://img.shields.io/github/stars/preprocessy/preprocessy)](https://github.com/preprocessy/preprocessy/stargazers)\n[![GitHub contributors](https://img.shields.io/github/contributors/preprocessy/preprocessy)](https://gitHub.com/preprocessy/preprocessy/graphs/contributors/)\n[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)\n[![MIT license](https://img.shields.io/badge/License-MIT-informational.svg)](https://lbesson.mit-license.org/)\n\nPreprocessy is a library that provides data preprocessing pipelines for machine learning. It bundles all the common preprocessing steps that are performed on the data to prepare it for machine learning models. It aims to do so in a manner that is independent of the source and type of dataset. Hence, it provides a set of functions that have been generalised to different types of data.\n\nThe pipelines themselves are composed of these functions and flexible so that the users can customise them by adding their processing functions or removing pipeline functions according to their needs. The pipelines thus provide an abstract and high-level interface to the users.\n\n## Pipeline Structure\n\nThe pipelines are divided into 3 logical stages -\n\n### Stage 1 - Pipeline Input\n\nInput datasets with the following extensions are supported - `.csv, .tsv, .xls, .xlsx, .xlsm, .xlsb, .odf, .ods, .odt`\n\n### Stage 2 - Processing\n\nThis is the major part of the pipeline consisting of processing functions. The following functions are provided out of the box as individual functions as well as a part of the pipelines -\n\n- Handling Null Values\n- Handling Outliers\n- Normalisation and Scaling\n- Label Encoding\n- Correlation and Feature Extraction\n- Training and Test set splitting\n\n### Stage 3 - Pipeline Output\n\nThe output consists of processed dataset and pipeline parameters depending on the verbosity required.\n\n## Contributing\n\nPlease read our [Contributing Guide](https://github.com/preprocessy/preprocessy/blob/master/CONTRIBUTING.md) before submitting a Pull Request to the project.\n\n## Support\n\nFeel free to contact any of the maintainers. We're happy to help!\n\n## Roadmap\n\nCheck out our [roadmap](https://github.com/preprocessy/preprocessy/projects/1) to stay informed of the latest features released and the upcoming ones. Feel free to give us your insights!\n\n## Documentation\n\nCurrently, documentation is under development. All contributions are welcome! Please see our [Contributing Guide](https://github.com/preprocessy/preprocessy/blob/master/CONTRIBUTING.md).\n\n## License\n\nSee the [LICENSE](https://github.com/preprocessy/preprocessy/blob/master/LICENSE) file for licensing information.\n\n## Links\n\n- Documentation: https://preprocessy.readthedocs.io/en/latest/\n- Changes: https://preprocessy.readthedocs.io/en/latest/changes/\n- PyPI Releases: https://pypi.org/project/preprocessy/\n- Source Code: https://github.com/preprocessy/preprocessy\n- Issue Tracker: https://github.com/preprocessy/preprocessy/issues\n- Chat: https://discord.gg/5q2yCqqU6N\n",
    'author': 'Saif Kazi',
    'author_email': 'saif1204kazi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://preprocessy.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
