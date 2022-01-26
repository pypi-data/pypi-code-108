# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glyles', 'glyles.glycans', 'glyles.glycans.factory', 'glyles.grammar']

package_data = \
{'': ['*']}

install_requires = \
['antlr4-python3-runtime>=4.9.3,<5.0.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pydot>=1.4.2,<2.0.0',
 'rdkit-pypi>=2021.9.2,<2022.0.0']

setup_kwargs = {
    'name': 'glyles',
    'version': '0.2.0',
    'description': 'A tool to convert IUPAC representation of glycans into SMILES strings',
    'long_description': '# GlyLES\n\nA tool to convert IUPAC representation of Glycans into SMILES representation. This repo is still in the development \nphase; so, feel free to report any errors or issues.\n\n## Specification and (current) Limitations\n\nThe exact specification, we\'re referring to when talking about "IUPAC representations of glycan", is given in the \n"Notes" section of this [website](https://www.ncbi.nlm.nih.gov/glycans/snfg.html). But as this package is still in the \ndevelopment phase, not everything of the specification is implemented yet (especially not all monomers and side chains \nyou can attach to monomers).\n\nThis implementation currently only works for glycans that fulfil certain properties:\n\n* Linkages have to be explicit, i.e. `(a1-4)`\n* The structure of the glycan can be represented as tree of the monomers with maximal branching factor 2.\n* All root monomers (e.g. Glc, but not GlcNAc) from this [website](https://www.ncbi.nlm.nih.gov/glycans/snfg.html)\n* Some modifications can be added to the monomers, please see the [README](glyles/grammar/README.md) in the grammar\nfolder for more information on this. \n\n## Installation\n\nSo far, this package can only be downloaded from the python package index. So the installation with `pip` is very easy.\nJust type\n\n``````shell\npip install glyles\n``````\n\nand you\'re ready to use it as described below. Use \n\n````shell\npip install --upgrade glyles\n````\n\nto upgrade the glyles package to the most recent version.\n\n## Workflow\n\nConvert the IUPAC into a SMILES representation using the handy `convert` method\n\n``````python\nfrom glyles.converter import convert\n\nconvert(glycan="Man(a1-2)Man", output_file="./test.txt")\n``````\n\nYou can also use the `convert_generator` method to get generator over all SMILES:\n\n``````python\nfrom glyles.converter import convert_generator\n\nfor smiles in convert_generator(glycan_list=["Man(a1-2)Man a", "Man(a1-2)Man b"]):\n    print(smiles)\n``````\n\nIn general, the `convert` and `convert_generator` methods supports the same for types of input. The samples are shown\nfor `convert` but it\'s the same for `convert_generator`.\n\n* single glycan, e.g. `convert(glycan="Man(a1-2)Man)"`,\n* a list of glycans, e.g. `convert(glycan_list=["Man(a1-2)Man a", "Man(a1-2)Man"])`, and\n* a file of glycans, e.g. `convert(glycan_file="./glycans.txt")`. Here its important that the file many only contain one\n  IUPAC per line.\n* for better runtime one can also provide a generator as input, e.g. `convert(glycan_generator=some_generator)`\n\nThe output for `convert` can be manifold as well. For `convert_generator` there is one output. `convert` supports\n\n* `stdout` when specifying no output-related argument, or\n* returned as list of tuples if `returning=true` is set, or\n* writing to an `output_file`, e.g. `convert(glycan="Man(a1-2)Man", output_file="./out.csv")`.\n\nHere each line of the output will state the input IUPAC and the output SMILES. In case of written output separated with \na comma.\n\n\n## Poetry\n\nTo develop this package I used the poetry package manager (see [here](https://python-poetry.org/) for a detailed\ninstruction). It has basically the same functionality as conda but supports the package management better and also \nsupports distinguishing packages into those that are needed to use the package and those that are needed in the \ndevelopment of the package. In order to enable others to work on this repository, we also publish the exact \nspecifications of out poetry environment.\n',
    'author': 'Roman Joeres',
    'author_email': 'Roman.Joeres@helmholtz-hzi.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
