# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rascore',
 'rascore.util.PDBrenum',
 'rascore.util.PDBrenum.src.download',
 'rascore.util.PDBrenum.src.renum.PDB',
 'rascore.util.PDBrenum.src.renum.mmCIF',
 'rascore.util.PDBrenum.src.renum.shared',
 'rascore.util.constants',
 'rascore.util.functions',
 'rascore.util.pages',
 'rascore.util.pipelines',
 'rascore.util.scripts']

package_data = \
{'': ['*'],
 'rascore': ['.streamlit/*',
             'util/*',
             'util/data/*',
             'util/data/rascore_cluster/*',
             'util/data/rascore_cluster/SW1/*',
             'util/data/rascore_cluster/SW1/SW1_0P/*',
             'util/data/rascore_cluster/SW1/SW1_2P/*',
             'util/data/rascore_cluster/SW1/SW1_3P/*',
             'util/data/rascore_cluster/SW2/*',
             'util/data/rascore_cluster/SW2/SW2_0P/*',
             'util/data/rascore_cluster/SW2/SW2_2P/*',
             'util/data/rascore_cluster/SW2/SW2_3P/*'],
 'rascore.util.PDBrenum': ['src/*', 'src/renum/*']}

install_requires = \
['Bio==1.3.3',
 'CairoSVG==2.5.2',
 'Pillow==9.0.0',
 'lxml==4.6.5',
 'matplotlib==3.3.4',
 'matplotlib_venn==0.11.6',
 'numpy==1.21',
 'pandas==1.4.0',
 'pendulum==2.1.2',
 'py3Dmol==1.8.0',
 'pyfiglet==0.8.post1',
 'rdkit_pypi==2021.9.4',
 'requests==2.25.1',
 'scipy==1.6.2',
 'seaborn==0.11.1',
 'statannot==0.2.3',
 'statsmodels==0.13.1',
 'stmol==0.0.7',
 'streamlit==1.4.0',
 'tqdm==4.59.0']

entry_points = \
{'console_scripts': ['rascore = rascore.rascore_cli:cli']}

setup_kwargs = {
    'name': 'rascore',
    'version': '0.1.34',
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
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
