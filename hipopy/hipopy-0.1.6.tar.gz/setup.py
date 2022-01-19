# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hipopy']

package_data = \
{'': ['*']}

install_requires = \
['awkward>=1.3.0,<2.0.0', 'numpy>=1.19.2,<2.0.0']

setup_kwargs = {
    'name': 'hipopy',
    'version': '0.1.6',
    'description': 'UpROOT-Like I/O Interface for CLAS12 HIPO Files',
    'long_description': '# HIPOPy: UpROOT-like I/O Interface for CLAS12 HIPO Files\n\n## Installation\n\nTo install from source:\n```bash\ngit --recurse-submodules clone https://github.com/mfmceneaney/hippy.git\ncd hippy\ncd hipo; cd lz4; make CFLAGS=-fPIC; cd ..; cmake .; make; cd ..\n```\nThen add to following to your startup script:\n```bash\nexport PYTHONPATH=$PYTHONPATH:/path/to/hipopy\n```\n\nTo install with pip:\n```bash\npip install hipopy\n```\n\n## Getting Started\n\nCheck out the example scripts in `tutorials`.  More functionality coming soon!\n\n#\n\nContact: matthew.mceneaney@duke.edu\n',
    'author': 'Matthew McEneaney',
    'author_email': 'matthew.mceneaney@duke.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mfmceneaney/hipopy.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
