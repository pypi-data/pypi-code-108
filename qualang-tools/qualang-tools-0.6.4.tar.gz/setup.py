# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qualang_tools',
 'qualang_tools.bakery',
 'qualang_tools.config',
 'qualang_tools.config.server',
 'qualang_tools.control_panel']

package_data = \
{'': ['*']}

install_requires = \
['dash-bootstrap-components>=1.0.0,<2.0.0',
 'dash-core-components>=2.0.0,<3.0.0',
 'dash-cytoscape>=0.3.0,<0.4.0',
 'dash-dangerously-set-inner-html>=0.0.2,<0.0.3',
 'dash-html-components>=2.0.0,<3.0.0',
 'dash-table>=5.0.0,<6.0.0',
 'dash>=2.0.0,<3.0.0',
 'docutils>=0.18.1,<0.19.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'qm-qua>=0.3.2,<0.4.0',
 'scipy>=1.7.1,<2.0.0',
 'waitress>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'qualang-tools',
    'version': '0.6.4',
    'description': 'The qualang_tools package includes various tools related to QUA programs in Python',
    'long_description': "# QUA Language Tools\n\nThe QUA language tools package includes various tools useful while writing QUA programs and performing experiments.\n\nIt includes:\n\n- The baking tool which allows defining waveforms in a QUA-like manner with for working with a 1ns resolution.  It can also be used to create even higher resolution waveforms.\n- Tools for converting a list of integration weights into the format used in the configuration.\n- Tools for creating waveforms commonly used in Quantum Science.\n- Tools for correcting mixer imbalances.\n\n## Support and Contribution\nHave an idea for another tool? A way to improve an existing one? Found a bug in our code?\n\nWe'll be happy if you could let us know by opening an [issue](https://github.com/qua-platform/py-qua-tools/issues) on the [GitHub repository](https://github.com/qua-platform/py-qua-tools).\n\nFeel like contributing code to this library? We're thrilled! Please follow [this guide](https://github.com/qua-platform/py-qua-tools/blob/main/CONTRIBUTING.md) and feel free to contact us if you need any help, you can do it by opening an [issue](https://github.com/qua-platform/py-qua-tools/issues) :)\n\n## Installation\n\nInstall the current version using `pip`, the `--upgrade` flag ensures that you will get the latest version.\n\n```\npip install --upgrade qualang-tools\n```\n\n## Usage\n\nExamples for using various tools can be found on the [QUA Libraries Repository](https://github.com/qua-platform/qua-libs).\n\nExamples for using the Baking toolbox, including 1-qubit randomized benchmarking, cross-entropy benchmark (XEB), high sampling rate baking and more can be found [here](https://github.com/qua-platform/qua-libs/tree/main/examples/bakery).\n",
    'author': 'QM',
    'author_email': 'qua-libs@quantum-machines.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qua-platform/py-qua-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
