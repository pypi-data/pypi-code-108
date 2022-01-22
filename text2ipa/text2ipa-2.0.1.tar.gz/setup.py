# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['text2ipa']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'text2ipa',
    'version': '2.0.1',
    'description': 'Convert text to IPA for English and French',
    'long_description': '<p align="center">\n<img src="https://raw.githubusercontent.com/tquangsdh20/text2ipa/master/.github/logo.svg">\n<img src="https://github.com/tquangsdh20/text2ipa/actions/workflows/test.yml/badge.svg?style=plastic"> <a href="https://app.codecov.io/gh/tquangsdh20/text2ipa/blob/af74004d58fb4cde15ea29b1184fc7a025ca9fc2/text2ipa/__main__.py"><img src="https://codecov.io/gh/tquangsdh20/text2ipa/branch/master/graphs/badge.svg?branch=master"></a> <img src="https://img.shields.io/pypi/implementation/text2ipa"> <img src = "https://img.shields.io/pypi/pyversions/text2ipa"> <img src="https://img.shields.io/badge/author-tquangsdh20-orange">\n</p>\n\n\n\n## Installation:\n\n**Windows**\n```\npython -m pip install text2ipa\n```\n**macOS**\n```\nsudo pip3 install text2ipa\n```\n**Linux**\n```\npip install text2ipa\n```\n\n## Features\n\n- Convert English text to IPA using the [toPhonetic](https://tophonetics.com/)\n- Three options Language English UK, English US and French\n  \n## Examples\n\n### Example 1: Convert a text\n\n#### Function: \n- `get_IPA()` : Converting a text to IPA with the following parameters \n\n#### Parameters:\n\n- `text` : The text you want to convert to IPA\n- `language` : Choose between English US, English UK and French (\'am\', \'br\' or \'fr\')\n- `proxy` : Optional parameter  \n\n#### For instance:\n\n```python\nfrom text2ipa import get_IPA\n# Convert \'hello world\' to English US International Alphabet\ntext = \'hello world\'\nlanguage = \'am\'\nipa = get_IPA(text, language)\n# Convert \'je parle un peu français\' to IPA\ntext = \'je parle un peu français\'\nlanguage = \'fr\'\nfr_ipa = get_IPA(text, language)\nprint(ipa)\nprint(fr_ipa)\n```\n```\n>> həˈloʊ wɜrld\n>> ʒə paʀle œ̃ pø fʀɑ̃̃sɛ\n```\n\n### Example 2: Convert a bulk\n\n#### Function: \n- `get_IPAs()` : Convert the list of texts to IPA return the list of IPAs \n\n#### Parameters:\n\n- `bulk` : The list of text want to convert to IPA\n- `language` : Choose between English US and English UK (\'am\'/\'br\')\n- `proxy` : Optional parameter  \n\n#### For instance:\n\n```python\nfrom text2ipa import get_IPAs\nbulk = [\'how are you?\',\'how it\\\'s going?\',\'that\\\'s good\']\nlanguage = \'br\'\n# Convert a list of text to English UK IPA\nIPAs = get_IPAs(bulk,language)\nfor ipa in IPAs:\n    print(ipa)\n```\n\n```\n>> haʊ ɑː juː?\n>> haʊ ɪts ˈgəʊɪŋ?\n>> ðæts gʊd\n```\n\n#### Log Changes\n\nV1.0.0 : Create new with 2 functions `get_IPA()` and `get_IPAs()`  \nV1.2.0 : Update comment and guideline in functions, fixed ERROR for setup with the other Python versions  \nV1.3.0 : Fixed MISSING install requires and update information for Python versions  \nV1.4.0 : Update building & testing for this package  \nV1.4.1 : Fixed Error Import `get_IPA()` and `get_IPAs`  \nV2.0.1 : New feature working with French\n\n<a href="https://github.com/tquangsdh20/text2ipa"><p align="center"><img src="https://img.shields.io/badge/Github-tquangsdh20-orange?style=social&logo=github"></p></a>\n',
    'author': 'Joseph Quang',
    'author_email': 'tquangsdh20@hcmut.edu.vn',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tquangsdh20/text2ipa',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
