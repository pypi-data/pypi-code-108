# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['benchmarks',
 'examples',
 'pyshacl',
 'pyshacl.assets',
 'pyshacl.constraints',
 'pyshacl.constraints.advanced',
 'pyshacl.constraints.core',
 'pyshacl.constraints.sparql',
 'pyshacl.extras',
 'pyshacl.extras.js',
 'pyshacl.functions',
 'pyshacl.helper',
 'pyshacl.inference',
 'pyshacl.monkey',
 'pyshacl.rdfutil',
 'pyshacl.rules',
 'pyshacl.rules.sparql',
 'pyshacl.rules.triple',
 'test',
 'test.issues',
 'test.issues.test_029',
 'test.issues.test_040',
 'test.test_js']

package_data = \
{'': ['*'],
 'test': ['resources/cmdline_tests/*',
          'resources/dash_tests/core/complex/*',
          'resources/dash_tests/core/misc/*',
          'resources/dash_tests/core/node/*',
          'resources/dash_tests/core/path/*',
          'resources/dash_tests/core/property/*',
          'resources/dash_tests/core/targets/*',
          'resources/dash_tests/expression/*',
          'resources/dash_tests/function/*',
          'resources/dash_tests/rules/sparql/*',
          'resources/dash_tests/rules/triple/*',
          'resources/dash_tests/shapedefs/*',
          'resources/dash_tests/sparql/component/*',
          'resources/dash_tests/sparql/node/*',
          'resources/dash_tests/sparql/property/*',
          'resources/dash_tests/target/*',
          'resources/js/*',
          'resources/sht_tests/*',
          'resources/sht_tests/core/*',
          'resources/sht_tests/core/complex/*',
          'resources/sht_tests/core/misc/*',
          'resources/sht_tests/core/node/*',
          'resources/sht_tests/core/path/*',
          'resources/sht_tests/core/property/*',
          'resources/sht_tests/core/targets/*',
          'resources/sht_tests/core/validation-reports/*',
          'resources/sht_tests/sparql/*',
          'resources/sht_tests/sparql/component/*',
          'resources/sht_tests/sparql/node/*',
          'resources/sht_tests/sparql/pre-binding/*',
          'resources/sht_tests/sparql/property/*']}

install_requires = \
['owlrl>=6.0.2,<7', 'prettytable>=2.2.1,<3.0.0', 'rdflib>=6.1.1,<8']

extras_require = \
{'dev-lint': ['flake8>=3.8.0,<4.0.0', 'isort>=5.7.0,<6.0.0', 'black==21.9b0'],
 'dev-type-checking': ['mypy>=0.800,<0.801', 'types-setuptools'],
 'js': ['pyduktape2>=0.4.1,<0.5.0'],
 'jsonld': ['rdflib-jsonld>=0.4.0,<0.6']}

entry_points = \
{'console_scripts': ['pyshacl = pyshacl.cli:main']}

setup_kwargs = {
    'name': 'pyshacl',
    'version': '0.18.1',
    'description': 'Python SHACL Validator',
    'long_description': '![](pySHACL-250.png)\n\n# pySHACL\nA Python validator for SHACL.\n\n[![Build Status](https://drone.rdflib.ashs.dev/api/badges/RDFLib/pySHACL/status.svg)](https://drone.rdflib.ashs.dev/RDFLib/pySHACL)\n\n[![DOI](https://zenodo.org/badge/147505799.svg)](https://zenodo.org/badge/latestdoi/147505799) [![Downloads](https://pepy.tech/badge/pyshacl)](https://pepy.tech/project/pyshacl) [![Downloads](https://pepy.tech/badge/pyshacl/month)](https://pepy.tech/project/pyshacl/month) [![Downloads](https://pepy.tech/badge/pyshacl/week)](https://pepy.tech/project/pyshacl/week)\n\nThis is a pure Python module which allows for the validation of [RDF](https://www.w3.org/2001/sw/wiki/RDF) graphs against Shapes Constraint Language ([SHACL](https://www.w3.org/TR/shacl/)) graphs. This module uses the [rdflib](https://github.com/RDFLib/rdflib) Python library for working with RDF and is dependent on the [OWL-RL](https://github.com/RDFLib/OWL-RL) Python module for [OWL2 RL Profile](https://www.w3.org/TR/owl2-overview/#ref-owl-2-profiles) based expansion of data graphs.\n\nThis module is developed to adhere to the SHACL Recommendation:\n> Holger Knublauch; Dimitris Kontokostas. *Shapes Constraint Language (SHACL)*. 20 July 2017. W3C Recommendation. URL: <https://www.w3.org/TR/shacl/> ED: <https://w3c.github.io/data-shapes/shacl/>\n\n# Community for Help and Support\nThe SHACL community has a discord server for discussion of topics around SHACL and the SHACL specification.\n\n[Use this invitation link: https://discord.gg/RTbGfJqdKB to join the server](https://discord.gg/RTbGfJqdKB)\n\nThere is a \\#pyshacl channel in which discussion around this python library can held, and you can ask for general pyshacl help too.\n\n## Installation\nInstall with PIP (Using the Python3 pip installer `pip3`)\n```bash\n$ pip3 install pyshacl\n```\n\nOr in a python virtualenv _(these example commandline instructions are for a Linux/Unix based OS)_\n```bash\n$ python3 -m virtualenv --python=python3 --no-site-packages .venv\n$ source ./.venv/bin/activate\n$ pip3 install pyshacl\n```\n\nTo exit the virtual enviornment:\n```bash\n$ deactivate\n```\n\n## Command Line Use\nFor command line use:\n_(these example commandline instructions are for a Linux/Unix based OS)_\n```bash\n$ pyshacl -s /path/to/shapesGraph.ttl -m -i rdfs -a -j -f human /path/to/dataGraph.ttl\n```\nWhere\n - `-s` is an (optional) path to the shapes graph to use\n - `-e` is an (optional) path to an extra ontology graph to import\n - `-i` is the pre-inferencing option\n - `-f` is the ValidationReport output format (`human` = human-readable validation report)\n - `-m` enable the meta-shacl feature\n - `-a` enable SHACL Advanced Features\n - `-j` enable SHACL-JS Features (if `pyhsacl[js]` is installed)\n\nSystem exit codes are:\n`0` = DataGraph is Conformant\n`1` = DataGraph is Non-Conformant\n`2` = The validator encountered a RuntimeError (check stderr output for details)\n`3` = Not-Implemented; The validator encountered a SHACL feature that is not yet implemented.\n\nFull CLI Usage options:\n```bash\n$ pyshacl -h\n$ python3 -m pyshacl -h\nusage: pyshacl [-h] [-s [SHACL]] [-e [ONT]] [-i {none,rdfs,owlrl,both}] [-m]\n               [--imports] [--abort] [-a] [-j] [-d] [-f {human,table,turtle,xml,json-ld,nt,n3}]\n               [-df {auto,turtle,xml,json-ld,nt,n3}]\n               [-sf {auto,turtle,xml,json-ld,nt,n3}]\n               [-ef {auto,turtle,xml,json-ld,nt,n3}] [-V] [-o [OUTPUT]]\n               DataGraph\n\nRun the pySHACL validator from the command line.\n\npositional arguments:\n  DataGraph             The file containing the Target Data Graph.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -s [SHACL], --shacl [SHACL]\n                        A file containing the SHACL Shapes Graph.\n  -e [ONT], --ont-graph [ONT]\n                        A file path or URL to a document containing extra\n                        ontological information to mix into the data graph.\n  -i {none,rdfs,owlrl,both}, --inference {none,rdfs,owlrl,both}\n                        Choose a type of inferencing to run against the Data\n                        Graph before validating.\n  -m, --metashacl       Validate the SHACL Shapes graph against the shacl-\n                        shacl Shapes Graph before validating the Data Graph.\n  --imports             Allow import of sub-graphs defined in statements with\n                        owl:imports.\n  -a, --advanced        Enable support for SHACL Advanced Features.\n  -j, --js              Enable support for SHACL-JS Features.\n  -it, --iterate-rules  Interate SHACL Rules until steady state is found (only available in Advanced Mode)\n  --abort               Abort on first error.\n  -d, --debug           Output additional runtime messages, including violations that didn\\\'t\n                        lead to non-conformance.\n  -f {human,turtle,xml,json-ld,nt,n3}, --format {human,turtle,xml,json-ld,nt,n3}\n                        Choose an output format. Default is "human".\n  -df {auto,turtle,xml,json-ld,nt,n3}, --data-file-format {auto,turtle,xml,json-ld,nt,n3}\n                        Explicitly state the RDF File format of the input\n                        DataGraph file. Default="auto".\n  -sf {auto,turtle,xml,json-ld,nt,n3}, --shacl-file-format {auto,turtle,xml,json-ld,nt,n3}\n                        Explicitly state the RDF File format of the input\n                        SHACL file. Default="auto".\n  -ef {auto,turtle,xml,json-ld,nt,n3}, --ont-file-format {auto,turtle,xml,json-ld,nt,n3}\n                        Explicitly state the RDF File format of the extra\n                        ontology file. Default="auto".\n  -V, --version         Print the PySHACL version and exit.\n  -o [OUTPUT], --output [OUTPUT]\n                        Send output to a file (defaults to stdout).\n```\n\n## Python Module Use\nFor basic use of this module, you can just call the `validate` function of the `pyshacl` module like this:\n\n```python\nfrom pyshacl import validate\nr = validate(data_graph,\n      shacl_graph=sg,\n      ont_graph=og,\n      inference=\'rdfs\',\n      abort_on_first=False,\n      allow_warnings=False,\n      meta_shacl=False,\n      advanced=False,\n      js=False,\n      debug=False)\nconforms, results_graph, results_text = r\n```\n\nWhere:\n* `data_graph` is an rdflib `Graph` object or file path of the graph to be validated\n* `shacl_graph` is an rdflib `Graph` object or file path or Web URL of the graph containing the SHACL shapes to validate with, or None if the SHACL shapes are included in the data_graph.\n* `ont_graph` is an rdflib `Graph` object or file path or Web URL a graph containing extra ontological information, or None if not required.\n* `inference` is a Python string value to indicate whether or not to perform OWL inferencing expansion of the `data_graph` before validation.\nOptions are \'rdfs\', \'owlrl\', \'both\', or \'none\'. The default is \'none\'.\n* `abort_on_first` (optional) `bool` value to indicate whether or not the program should abort after encountering the first validation failure or to continue. Default is to continue.\n* `allow_warnings` (optional) `bool` value, Shapes marked with severity of Warning or Info will not cause result to be invalid. \n* `meta_shacl` (optional) `bool` value to indicate whether or not the program should enable the Meta-SHACL feature. Default is False.\n* `advanced`: (optional) `bool` value to enable SHACL Advanced Features\n* `js`: (optional) `bool` value to enable SHACL-JS Features (if `pyshacl[js]` is installed)\n* `debug` (optional) `bool` value to indicate whether or not the program should emit debugging output text, including violations that didn\'t lead to non-conformance overall. So when debug is True don\'t judge conformance by absense of violation messages. Default is False.\n\nSome other optional keyword variables available on the `validate` function:\n* `data_graph_format`: Override the format detection for the given data graph source file.\n* `shacl_graph_format`: Override the format detection for the given shacl graph source file.\n* `ont_graph_format`: Override the format detection for the given extra ontology graph source file.\n* `iterate_rules`: Interate SHACL Rules until steady state is found (only works with advanced mode).\n* `do_owl_imports`: Enable the feature to allow the import of subgraphs using `owl:imports` for the shapes graph and the ontology graph. Note, you explicitly cannot use this on the target data graph.\n* `serialize_report_graph`: Convert the report results_graph into a serialised representation (for example, \'turtle\')\n* `check_dash_result`: Check the validation result against the given expected DASH test suite result.\n* `check_sht_result`: Check the validation result against the given expected SHT test suite result.\n\nReturn value:\n* a three-component `tuple` containing:\n  * `conforms`: a `bool`, indicating whether or not the `data_graph` conforms to the `shacl_graph`\n  * `results_graph`: a `Graph` object built according to the SHACL specification\'s [Validation Report](https://www.w3.org/TR/shacl/#validation-report) structure\n  * `results_text`: python string representing a verbose textual representation of the [Validation Report](https://www.w3.org/TR/shacl/#validation-report)\n\n\n## Python Module Call\n\nYou can get an equivalent of the Command Line Tool using the Python3 executable by doing:\n\n```bash\n$ python3 -m pyshacl\n```\n\n\n## Errors\nUnder certain circumstances pySHACL can produce a `Validation Failure`. This is a formal error defined by the SHACL specification and is required to be produced as a result of specific conditions within the SHACL graph.\nIf the validator produces a `Validation Failure`, the `results_graph` variable returned by the `validate()` function will be an instance of `ValidationFailure`.\nSee the `message` attribute on that instance to get more information about the validation failure.\n\nOther errors the validator can generate:\n- `ShapeLoadError`: This error is thrown when a SHACL Shape in the SHACL graph is in an invalid state and cannot be loaded into the validation engine.\n- `ConstraintLoadError`: This error is thrown when a SHACL Constraint Component is in an invalid state and cannot be loaded into the validation engine.\n- `ReportableRuntimeError`: An error occurred for a different reason, and the reason should be communicated back to the user of the validator.\n- `RuntimeError`: The validator encountered a situation that caused it to throw an error, but the reason does concern the user.\n\nUnlike `ValidationFailure`, these errors are not passed back as a result by the `validate()` function, but thrown as exceptions by the validation engine and must be\ncaught in a `try ... except` block.\nIn the case of `ShapeLoadError` and `ConstraintLoadError`, see the `str()` string representation of the exception instance for the error message along with a link to the relevant section in the SHACL spec document.\n\n\n## Windows CLI\n\n[Pyinstaller](https://www.pyinstaller.org/) can be\n[used](https://pyinstaller.readthedocs.io/en/stable/usage.html) to create an\nexecutable for Windows that has the same characteristics as the Linux/Mac\nCLI program.\nThe necessary ``.spec`` file is already included in ``pyshacl/pyshacl-cli.spec``.\nThe ``pyshacl-cli.spec`` PyInstaller spec file creates a ``.exe`` for the\npySHACL Command Line utility. See above for the pySHACL command line util usage instructions.\n\nSee [the PyInstaller installation guide](https://pyinstaller.readthedocs.io/en/stable/installation.html#installing-in-windows) for info on how to install PyInstaller for Windows.\n\nOnce you have pyinstaller, use pyinstaller to generate the ``pyshacl.exe`` CLI file like so:\n```bash powershell\n$ cd src/pyshacl\n$ pyinstaller pyshacl-cli.spec\n```\nThis will output ``pyshacl.exe`` in the ``dist`` directory in ``src/pyshacl``.\n\nYou can now run the pySHACL Command Line utility via ``pyshacl.exe``.\nSee above for the pySHACL command line util usage instructions.\n\n\n## Compatibility\nPySHACL is a Python3 library. For best compatibility use Python v3.7 or greater. Python3 v3.6 or below is _**not supported**_ and this library _**does not work**_ on Python v2.7.x or below.\n\nPySHACL is now a PEP518 & PEP517 project, it uses `pyproject.toml` and `poetry` to manage dependencies, build and install.\n\nFor best compatibility when installing from PyPI with `pip`, upgrade to pip v18.1.0 or above.\n  - If you\'re on Ubuntu 16.04 or 18.04, you will need to run `sudo pip3 install --upgrade pip` to get the newer version.\n\n\n## Features\nA features matrix is kept in the [FEATURES file](https://github.com/RDFLib/pySHACL/blob/master/FEATURES.md).\n\n\n## Changelog\nA comprehensive changelog is kept in the [CHANGELOG file](https://github.com/RDFLib/pySHACL/blob/master/CHANGELOG.md).\n\n\n## Benchmarks\nThis project includes a script to measure the difference in performance of validating the same source graph that has been inferenced using each of the four different inferencing options. Run it on your computer to see how fast the validator operates for you.\n\n\n## License\nThis repository is licensed under Apache License, Version 2.0. See the [LICENSE deed](https://github.com/RDFLib/pySHACL/blob/master/LICENSE.txt) for details.\n\n\n## Contributors\nSee the [CONTRIBUTORS file](https://github.com/RDFLib/pySHACL/blob/master/CONTRIBUTORS.md).\n\n\n## Citation\nDOI: [10.5281/zenodo.4750840](https://doi.org/10.5281/zenodo.4750840) (For all versions/latest version)\n\n## Contacts\nProject Lead:\n**Nicholas Car**\n*Senior Experimental Scientist*\nCSIRO Land & Water, Environmental Informatics Group\nBrisbane, Qld, Australia\n<nicholas.car@csiro.au>\n<http://orcid.org/0000-0002-8742-7730>\n\nLead Developer:\n**Ashley Sommer**\n*Informatics Software Engineer*\nCSIRO Land & Water, Environmental Informatics Group\nBrisbane, Qld, Australia\n<Ashley.Sommer@csiro.au>\n<https://orcid.org/0000-0003-0590-0131>\n',
    'author': 'Ashley Sommer',
    'author_email': 'Ashley.Sommer@csiro.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/RDFLib/pySHACL',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
