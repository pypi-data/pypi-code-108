# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['functionwords']

package_data = \
{'': ['*'],
 'functionwords': ['resources/chinese_classical_comprehensive.json',
                   'resources/chinese_classical_comprehensive.json',
                   'resources/chinese_classical_comprehensive.json',
                   'resources/chinese_classical_comprehensive.json',
                   'resources/chinese_classical_comprehensive.json',
                   'resources/chinese_classical_comprehensive.json',
                   'resources/chinese_classical_naive.json',
                   'resources/chinese_classical_naive.json',
                   'resources/chinese_classical_naive.json',
                   'resources/chinese_classical_naive.json',
                   'resources/chinese_classical_naive.json',
                   'resources/chinese_classical_naive.json',
                   'resources/chinese_comprehensive.json',
                   'resources/chinese_comprehensive.json',
                   'resources/chinese_comprehensive.json',
                   'resources/chinese_comprehensive.json',
                   'resources/chinese_comprehensive.json',
                   'resources/chinese_comprehensive.json',
                   'resources/chinese_simplified_modern.json',
                   'resources/chinese_simplified_modern.json',
                   'resources/chinese_simplified_modern.json',
                   'resources/chinese_simplified_modern.json',
                   'resources/chinese_simplified_modern.json',
                   'resources/chinese_simplified_modern.json',
                   'resources/description.json',
                   'resources/description.json',
                   'resources/description.json',
                   'resources/description.json',
                   'resources/description.json',
                   'resources/description.json',
                   'resources/english.json',
                   'resources/english.json',
                   'resources/english.json',
                   'resources/english.json',
                   'resources/english.json',
                   'resources/english.json']}

setup_kwargs = {
    'name': 'functionwords',
    'version': '0.8',
    'description': 'Extract curated Chinese and English function words from texts.',
    'long_description': '# functionwords\n[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/)\n\nThe `functionwords` package provides **curated** Chinese and English function words.\nIt supports five function word lists, as listed below.\nChinese function words are only available in simplified form.\n\n\n|`Function_words_list`      |# of function words| &nbsp; &nbsp; &nbsp; &nbsp;Description &nbsp; &nbsp; &nbsp; &nbsp;|\n|:----:|:----:|:----|\n| `chinese_simplified_modern`      |  819   |compiled from the [dictionary][1]     |\n| `chinese_classical_naive`        |  32    |harvested from the [platforms][2]     |\n| `chinese_classical_comprehensive`|  466   |compiled from the [dictionary][3]     |\n| `chinese_comprehensive`          |  1,122 | a combination of `chinese_simplified_modern`, `chinese_classical_naive`, and `chinese_classical_comprehensive`|\n| `english`                        |  512   |found in  [software][4]               |\n\nThe `FunctionWords` class does the heavy lifting.\nInitiate it with the desired `function_words_list`.\nThe instance has two methods `transform()` and `get_feature_names()`) and\nthree attributes (`function_words_list`, `function_words`, and `description`).\n\nFor more details, see FunctionWords instance\'s attribute `description`.\n\n## Installation\n\n```bash\npip install -U functionwords\n```\n\n## Getting started\n\n\n```python\nfrom functionwords import FunctionWords\n\nraw = "The present King of Singapore is bald."\n\n# to instantiate a FunctionWords instance\n# `function_words_list` can be either \'chinese_classical_comprehensive\', \n# \'chinese_classical_naive\', \'chinese_simplified_modern\', or \'english\'\nfw = FunctionWords(function_words_list=\'english\')\n\n# to count function words accordingly\n# returns a list of counts\nfw.transform(raw)\n\n# to list all function words given `function_words_list`\n# returns a list\nfw.get_feature_names()\n\n```\n\n## Requirements\n\nOnly Python 3.8+ is required.\n\n## Important links\n\n- Source code: https://github.com/Wang-Haining/functionwords\n- Issue tracker: https://github.com/Wang-Haining/functionwords/issues\n\n## Version\n\n- Created on March 17, 2021. v.0.5, launch.\n- Modified on Nov. 19, 2021. v.0.6, fix bugs in extracting Chinese ngram features.\n- Modified on Jan. 03, 2022. v.0.7, add `chinese_comprehensive` feature set.\n- Modified on Jan. 23, 2022. v.0.8, count Chinese ngram features finely.\n\n## Licence\n\nThis package is licensed under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).\n\n## References\n[1]: Ziqiang, W. (1998). Modern Chinese Dictionary of Function Words. Shanghai Dictionary Press.\n\n[2]: https://baike.baidu.com/item/%E6%96%87%E8%A8%80%E8%99%9A%E8%AF%8D and \nhttps://zh.m.wikibooks.org/zh-hans/%E6%96%87%E8%A8%80/%E8%99%9B%E8%A9%9E\n\n[3]: Hai, W., Changhai, Z., Shan, H., Keying, W. (1996). Classical Chinese Dictionary of Function Words. Peking University Press.\n\n[4]: [Jstylo](https://github.com/psal/jstylo/blob/master/src/main/resources/edu/drexel/psal/resources/koppel_function_words.txt).\n\n',
    'author': 'Haining Wang',
    'author_email': 'hw56@indiana.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Wang-Haining/functionwords',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
