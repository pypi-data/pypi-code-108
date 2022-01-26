# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enginelib',
 'enginelib.decor',
 'enginelib.matchers',
 'enginelib.matchers.same_patient',
 'enginelib.matchers.same_provider',
 'enginelib.mpe',
 'enginelib.mpe.subtrees',
 'enginelib.mpe.utils',
 'enginelib.rds']

package_data = \
{'': ['*']}

install_requires = \
['deprecation>2.0',
 'fhir.resources>=6.1.0,<7.0.0',
 'insight-engine-schema-python>=0,<1',
 'rialtic-data-dev-py<2',
 'sphinx>=4.1.2,<5.0.0']

setup_kwargs = {
    'name': 'rialtic-engine-lib-py',
    'version': '1.11.5',
    'description': 'Python Library for development of Rialtic Insight Engines',
    'long_description': '# Rialtic Engine Development Library (Python)\n\nThis repository contains common modules for developing Rialtic Insight Engines with Python.\n\n## API Documentation (Sphinx)\n\nThe code in this repository is documented using [`sphinx`](https://www.sphinx-doc.org/en/master/) and\n[`autodoc`](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc). This\ndocumentation can be generated locally. `autodoc` will generate basic documentation automatically from code, and\ndocstrings in the code can be used to add additional information to the generated documentation.\n\n### Documentation Practices\n\n#### Docstring Format\n\nWe use `sphinx.ext.napoleon`, which allows us to use a simpler, more concise format for docstrings\n(popularized by NumPy and Google projects). See\nthe [NumPy documentation](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard)\nfor an overview of how to use this style of docstrings.\n\n**NOTE:** One main way that our docs differ from the standard described in the NumPy docs is with regard to\nthe `Returns` section. We do not need to specify return type in our docs—we have the\n`sphinx_autodoc_typehints` extension, which automatically reads return type from type annotations in code.\n\n#### Docstring Guidelines\n\nAny docstrings written will eventually need to be edited or rewritten. With this in mind, it is valuable for our\ndocstrings to be concise and minimal, providing only necessary information, to reduce the work required to maintain\nthese docs.\n\nFor simple methods and functions, the generated function signature docs may even be sufficient. In these cases a\ndocstring can consist of only a single line summary.\n\nIf you find yourself writing a very long complex docstring, consider whether the object being documented could use a\nrefactor, or needs to be simplified in some way.\n\n### Generating HTML Documentation Locally\n\nThe generated documentation will be hosted somewhere accessible on the web, but can also be generated locally in several\nformats including HTML and PDF. Follow the instructions below to generate HTML documentation locally:\n\n1.  ```bash\n    $ git clone git@github.com:rialtic-community/rialtic-engine-lib-py.git\n    $ cd rialtic-engine-lib-py/docs\n    $ make html\n    ```\n    \n2. Open the following file in a browser\n    ```bash\n\n    rialtic-engine-lib-py/docs/_build/html/index.html\n    ```\n',
    'author': 'Rialtic',
    'author_email': 'engines.data@rialtic.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rialtic.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
