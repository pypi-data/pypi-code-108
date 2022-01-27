# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['chemcalculator', 'chemcalculator.data']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'chemcalculator',
    'version': '0.1.2',
    'description': 'Calculate chemical formula mass or atomic mass (g/mol), convert moles to grams and grams to moles, and calculate percentage mass for chemical or atom of interest',
    'long_description': '# chemcalculator\n\n\n## Overview \n\nchemcalculator is a python package useful for chemistry for purpose of calculating chemical formular mass in g/mol. The mole allows scientists to calculate the number of elementary entities (usually atoms or molecules) in a certain mass of a given substance. Another property of Avogadro’s number is that the mass of one mole of a substance is equal to that substance’s molecular weight. For example, the mean molecular weight of water is 18.015 atomic mass units (amu), so one mole of water weighs 18.015 grams. This property simplifies many chemical computations. This python package will be helpful to easily calculate the chemical formula mass, convert moles to grams and vice versa, and lastly calculate the percentage mass for the atomic nature of the elements in chemistry.\n\nThis package of basic chemistry calculations is meant to supplement an existing package, [ChemPy](https://github.com/bjodah/chempy), which already handles complex calculations for primarily physical/inorganic/analytical chemistry consisting of, but not limited to, the following:\n\n- Solver for equilibria (including multiphase systems)\n- Numerical integration routines for chemical kinetics (ODE solver front-end)\n- Integrated rate expressions (and convenience fitting routines)\n- Relations in Physical chemistry\n- Debye-Hückel expressions\n- Arrhenius equation\n- Einstein-Smoluchowski equation\n- Properties, such as : water density as function of temperature, water permittivity as function of temperature and pressure, and water diffusivity as function of temperature\n\n## Functions\n\nThis package contains three functions. Each function will have it\'s own required and optional arguments.\n\n1. `compute_mass`: Calculate the mass of the atoms or chemical formula for the input chemical formula.\n2. `moles_grams_converter`: Convert moles to grams and convert grams to moles.\n3. `percent_mass`: Calculate percentage mass for the desired atom or molecule.\n\n## Installation\n\n```bash\n$ pip install chemcalculator\n```\n\n## Usage\n\n`chemcalculator` can be used as follows:\n```bash\nfrom chemcalculator.chemcalculator import compute_mass\ncompute_mass("H2O")\n```\n```bash\nfrom chemcalculator.chemcalculator import moles_grams_converter\nmoles_grams_converter("H2O", 0.05555, "moles")\n```\n```bash\nfrom chemcalculator.chemcalculator import percent_mass\npercent_mass("H2O", "0")\n```\n\n## Contributors\n### Development Lead\n\n|Contributor Name     | GitHub Username|\n|---------------------|-----------|\n|Kingslin Lv | [Kingslin0810](https://github.com/Kingslin0810)|\n|Joyce Wang      | [jo4356](https://github.com/jo4356)     |\n|Allyson Stoll       | [datallurgy](https://github.com/datallurgy) |\n\nWe welcome and recognize all contributions. Please find the guide for contribution in [Contributing Document](https://github.com/UBC-MDS/chemcalculator/blob/main/CONTRIBUTING.md).\n\n## License\n\n`chemcalculator` was created by Joyce Wang, Kingslin Lv, Allyson Stoll. It is licensed under the terms of the MIT license.\n\n### Credits\n\nThis package was created with Cookiecutter and the UBC-MDS/cookiecutter-ubc-mds project template, modified from the [pyOpenSci/cookiecutter-pyopensci](https://github.com/pyOpenSci/cookiecutter-pyopensci) project template and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).\n',
    'author': 'Joyce Wang, Kinslin Lv, Allyson Stoll',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
