# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pearll',
 'pearll.agents',
 'pearll.buffers',
 'pearll.callbacks',
 'pearll.common',
 'pearll.explorers',
 'pearll.models',
 'pearll.signal_processing',
 'pearll.updaters']

package_data = \
{'': ['*']}

install_requires = \
['gym>=0.19.0,<0.20.0',
 'matplotlib>=3.5.0,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'tensorboard>=2.7.0,<3.0.0',
 'torch>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pearll',
    'version': '0.2.0',
    'description': 'Adaptable tools to make reinforcement learning and evolutionary computation algorithms',
    'long_description': None,
    'author': 'Rohan Tangri',
    'author_email': 'rohan.tangri@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
