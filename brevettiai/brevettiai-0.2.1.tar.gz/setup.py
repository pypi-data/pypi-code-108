# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brevettiai',
 'brevettiai.data',
 'brevettiai.data.image',
 'brevettiai.interfaces',
 'brevettiai.io',
 'brevettiai.model',
 'brevettiai.platform',
 'brevettiai.tests',
 'brevettiai.utils']

package_data = \
{'': ['*'], 'brevettiai.tests': ['bin/*']}

install_requires = \
['altair==4.1.0',
 'backoff>=1.10',
 'configparser>=5.0',
 'cryptography>=36.0.1,<37.0.0',
 'minio>=7.0,<7.1',
 'mmh3>=3.0',
 'numpy>=1.18.1',
 'pandas>=1.1,<1.2',
 'plotly>=4.14.3',
 'pydantic>=1.8.2',
 'requests>=2.23',
 'scikit-learn>=0.23.1',
 'shapely>=1.7.0',
 'tf2onnx>=1.9.0',
 'tqdm>=4.62']

extras_require = \
{'cv2': ['opencv-python>=4.1'],
 'cv2-headless': ['opencv-python-headless>=4.1'],
 'tf': ['tensorflow>=2.7,<2.8'],
 'tfa': ['tensorflow_addons>=0.15.0']}

setup_kwargs = {
    'name': 'brevettiai',
    'version': '0.2.1',
    'description': 'Brevetti AI library',
    'long_description': '# Brevetti AI core library\nThe brevettiai library enables integration with the brevetti.ai platform for development of training packages\n\nThe library is used as a API through the Job class with a number of utility functions for easy development of models.\nThe tools supports both local development on linux and windows as well as hosted training on e.g. Amazon Web Services sagemaker platform.\n\n## Contents\n\n* **brevettiai** Python package containing API and utility functions\n* **sample_model** Skeleton structure to build a package including definition and loading of model settings, simple dataset loading and job completion triggering.\n\nDeveloper documentation can be found at [docs.brevetti.ai](https://docs.brevetti.ai/)\n',
    'author': 'Emil Tyge',
    'author_email': 'emil@brevetti.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://bitbucket.org/criterionai/core.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
