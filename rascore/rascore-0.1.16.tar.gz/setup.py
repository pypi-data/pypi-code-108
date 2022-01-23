# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rascore',
 'rascore.scripts',
 'rascore.scripts.PDBrenum',
 'rascore.scripts.PDBrenum.src.download',
 'rascore.scripts.PDBrenum.src.renum.PDB',
 'rascore.scripts.PDBrenum.src.renum.mmCIF',
 'rascore.scripts.PDBrenum.src.renum.shared',
 'rascore.scripts.constants',
 'rascore.scripts.functions',
 'rascore.scripts.pages',
 'rascore.scripts.tools']

package_data = \
{'': ['*'],
 'rascore.scripts': ['data/*',
                     'data/rascore_cluster/*',
                     'data/rascore_cluster/SW1/*',
                     'data/rascore_cluster/SW1/SW1_0P/*',
                     'data/rascore_cluster/SW1/SW1_2P/*',
                     'data/rascore_cluster/SW1/SW1_3P/*',
                     'data/rascore_cluster/SW2/*',
                     'data/rascore_cluster/SW2/SW2_0P/*',
                     'data/rascore_cluster/SW2/SW2_2P/*',
                     'data/rascore_cluster/SW2/SW2_3P/*'],
 'rascore.scripts.PDBrenum': ['src/*', 'src/renum/*']}

install_requires = \
['Bio>=1.3.3',
 'CairoSVG>=2.5.2',
 'lxml>=4.6.3',
 'matplotlib>=3.3.4',
 'matplotlib_venn>=0.11.6',
 'numpy>=1.20.1',
 'pandas>=1.2.4',
 'pendulum>=2.1.2',
 'rdkit-pypi>=2021.9.4',
 'requests>=2.25.1',
 'scipy>=1.6.2',
 'seaborn>=0.11.1',
 'statannot>=0.2.3',
 'statsmodels>=0.12.2',
 'streamlit>=1.4.0',
 'tqdm>=4.59.0']

entry_points = \
{'console_scripts': ['rascore = rascore.rascore_cli:cli']}

setup_kwargs = {
    'name': 'rascore',
    'version': '0.1.16',
    'description': 'A tool for analyzing the conformations of RAS structures',
    'long_description': None,
    'author': 'mitch-parker',
    'author_email': 'mitch.isaac.parker@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
