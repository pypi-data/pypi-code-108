# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['idp_engine']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0', 'textX>=2.1.0,<3.0.0', 'z3-solver==4.8.12.0']

entry_points = \
{'console_scripts': ['idp-engine = idp_engine.IDP_Z3:cli']}

setup_kwargs = {
    'name': 'idp-engine',
    'version': '0.9.1',
    'description': 'IDP-Z3 is a reasoning engine for knowledge represented using the FO(.) (aka FO-dot) language.',
    'long_description': 'idp-engine is a reasoning engine for knowledge represented using the FO(.) language.\nFO(.) (aka FO-dot) is First Order logic, with various extensions to make it more expressive:  types, equality, arithmetic, inductive definitions, aggregates, and intensional objects.\nThe idp-engine uses the Z3 SMT solver as a back-end.\n\nIt is developed by the Knowledge Representation group at KU Leuven in Leuven, Belgium, and made available under the [GNU LGPL v3 License](https://www.gnu.org/licenses/lgpl-3.0.txt).\n\nSee more information at [www.IDP-Z3.be](https://www.IDP-Z3.be).\n\n\n# Installation\n\n``idp_engine`` can be installed from [pypi.org](https://pypi.org/), e.g. using [pip](https://pip.pypa.io/en/stable/user_guide/):\n\n```\n   pip install idp_engine\n```\n\n# Get started\n\nThe following code illustrates how to run inferences on a knowledge base.\n\n```\n    from idp_engine import IDP, model_expand\n    kb = IDP.parse("path/to/file.idp")\n    T, S = kb.get_blocks("T, S")\n    for model in model_expand(T,S):\n        print(model)\n```\n\nFor more information, please read [the documentation](http://docs.idp-z3.be/en/latest/).\n\n# Contribute\n\nContributions are welcome!  The repository is [on GitLab](https://gitlab.com/krr/IDP-Z3).',
    'author': 'pierre.carbonnelle',
    'author_email': 'pierre.carbonnelle@cs.kuleuven.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.idp-z3.be',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
