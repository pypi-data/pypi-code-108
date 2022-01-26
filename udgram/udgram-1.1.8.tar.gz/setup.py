# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['udgram']
install_requires = \
['conllu==4.4.1']

setup_kwargs = {
    'name': 'udgram',
    'version': '1.1.8',
    'description': '',
    'long_description': '# UDGram\nCompute probabilities in N-grams model for tags in UD format\n\n### Instalation\n  ...\n\n### Usage\n##### n-gram funcions\n  - `bigram`  : function for bigrams with specify tag\n  - `trigram` : function for trigrams with specify tag\n  - `ngram`   : general function for ngram with specify tag\n\n##### ngram matriz funcions\n  - `bigram_matriz`\t: matriz with bigram probabilities for tags\n  - `ngram_matriz`\t: matriz with ngram probabilities for tags\n\n\n### Contributors\n  - Wellington Silva [(@wellington36)](https://github.com/wellington36)\n',
    'author': 'wellington36',
    'author_email': 'wellington.71319@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>3.8',
}


setup(**setup_kwargs)
