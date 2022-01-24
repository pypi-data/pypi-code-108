# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['moped', 'moped.core', 'moped.topological', 'moped.utils']

package_data = \
{'': ['*']}

install_requires = \
['Meneco==1.5.3',
 'PyYAML>=6.0,<7.0',
 'cobra>=0.22.1,<0.23.0',
 'cycparser>=1.0.0,<2.0.0',
 'modelbase>=1.5.2,<2.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pipdeptree>=2,<3',
 'pyasp>=1.4.4,<2.0.0',
 'python-libsbml>=5.19.0,<6.0.0',
 'tqdm>=4,<5']

setup_kwargs = {
    'name': 'moped',
    'version': '1.9.3',
    'description': 'Stoichiometric metabolic modelling',
    'long_description': '[![pipeline status](https://gitlab.com/marvin.vanaalst/moped/badges/main/pipeline.svg)](https://gitlab.com/marvin.vanaalst/moped/-/commits/main)\n[![coverage report](https://gitlab.com/marvin.vanaalst/moped/badges/main/coverage.svg)](https://gitlab.com/marvin.vanaalst/moped/-/commits/main)\n[![Documentation Status](https://readthedocs.org/projects/moped/badge/?version=latest)](https://moped.readthedocs.io/en/latest/?badge=latest)\n[![PyPi](https://img.shields.io/pypi/v/moped)](https://pypi.org/project/moped/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n[![Downloads](https://pepy.tech/badge/moped)](https://pepy.tech/project/moped)\n\n# moped\n\nA metabolic object-oriented Python modelling environment.\n\n## Installation\n\nYou can install moped using pip\n\n`pip install moped`  \n\nHowever, you will still need to install NCBI Blast if you want to use the genome / proteome reconstruction methods\n\nIf you are using conda or mamba, you can install blast from bioconda: \n\n`conda install -c bioconda blast==2.12.0`  \n`mamba install -c bioconda blast==2.12.0`  \n\nIf you want to install BLAST yourself:\n- download the latest blast version from [NCBI](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)\n- Extract the downloaded folder to a path of your liking\n- Add blast to your path e.g. by adding the following line to your .bashrc\n  - `export PATH="your_blast_directory/bin:$PATH"`\n\n\n## Documentation\n\nCheck out our tutorial on [readthedocs](https://moped.readthedocs.io/en/latest/) \n\n\n## Contributing\n\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome.\nIf you want to contribute code to the project, please consider our [contribution guide](https://gitlab.com/marvin.vanaalst/moped/-/blob/main/CONTRIBUTING.md)\n\n## License\n\nmoped is licensed under [GPL 3](https://gitlab.com/marvin.vanaalst/moped/-/blob/main/LICENSE)\n\n## Issues and support\n\nIf you experience issues using the software please contact us through our [issues](https://gitlab.com/marvin.vanaalst/moped/issues) page.\n',
    'author': 'Marvin van Aalst',
    'author_email': 'marvin.vanaalst@gmail.com',
    'maintainer': 'Marvin van Aalst',
    'maintainer_email': 'marvin.vanaalst@gmail.com',
    'url': 'https://gitlab.com/marvin.vanaalst/moped',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
